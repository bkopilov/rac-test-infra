import copy
import json
import logging

from assisted_test_infra.test_infra import utils
from api_tests.common.disks import CleanNodeDisks


import pytest

import semver

from tests.base_test import BaseTest
from tests.config import global_variables

logger = logging.getLogger(__name__)

VIRTUALIZATION_BUNDLE = ['nmstate', 'cnv', 'lso', 'odf']
DISK_INSTALLATION_TYPE="SSD"
DISK_INSTALLATION_NAME = "nvme0n1" #assume exist on all machines


class TestBaremetalMachines(BaseTest):

    @staticmethod
    def _clean_disks(cluster):
        nodes = cluster.nodes
        for n in nodes:
            CleanNodeDisks(n).clean_disks()

    @staticmethod
    def _set_installation_disk(cluster, driver_type=DISK_INSTALLATION_TYPE, disk_name=DISK_INSTALLATION_NAME):
        # Update installation disks to SSD same on all machines
        # Driver type can be iSCSI or Multipath
        for host in cluster.get_details().hosts:
            host_info = {"id": host.id}
            disks = cluster.get_host_disks(host_info,
                                           lambda disk: disk['drive_type'] == driver_type and disk['name'] == disk_name)
            assert len(disks) == 1, "Expected 1 disk but got %d" % len(disks)
            first_installation_disk = json.loads(f'[{{"disk_id": "{disks[0]["id"]}", "role": "install"}}]')
            cluster.select_installation_disk(host_id=host_info['id'], disk_paths=first_installation_disk)

    @staticmethod
    def _set_bundle_operators(cluster, *operators):
        # Create operators bundle , remove duplicate
        operators_list = copy.deepcopy(VIRTUALIZATION_BUNDLE)
        operators_list.extend(operators)
        for operator in set(operators_list):
            cluster.set_olm_operator(operator)

    @staticmethod
    def nfs_servers():
        # Assume NFS server enabled on  /tmp/test_images/ - ip route get 1 | awk '{ printf  $7 }'
        command = """ip route get 1 | awk '{ printf  $7 }'"""
        cmd_out, _, _ = utils.run_command(command, shell=True)
        return cmd_out

    @staticmethod
    def _get_vip_ingress(ipv4_address, ingress=100, vip=101):
        """Set vip and ingress from machine network, pick unused

        Probabaly we get set here function - available_host_for_vip - TBD
        :param ipv4_address:
        :param ingress:
        :param vip:
        :return:
        """
        to_list_vip = ipv4_address.split(".")
        to_list_ingress = ipv4_address.split(".")
        to_list_vip[3] = str(vip)
        to_list_ingress[3] = str(ingress)
        return ".".join(to_list_vip), ".".join(to_list_ingress)

    @staticmethod
    def _set_roles_names(cluster, masters_count):
        # set hostname - >by default unamed
        host_role = "master"
        index = 0
        visit_all_masters = False  # in case we have more workers
        for host in cluster.get_hosts():
            cluster._infra_env.update_host(
                host_id=host["id"],
                host_role=host_role,
                host_name=f"{host_role}-{index}",
            )
            index += 1
            if not visit_all_masters and index == masters_count:
                visit_all_masters = True
                host_role = "worker"
                index = 0


    @pytest.mark.parametrize(
        "redfish_machines",
        [
            [
                "10.6.49.60",
                "10.6.49.61",
                "10.6.49.62",
                "10.6.49.63",
                "10.6.49.64",
                "10.6.49.65",
            ]
        ],
    )
    @pytest.mark.parametrize("redfish_user", ["root"])
    @pytest.mark.parametrize("redfish_enabled", [True])
    @pytest.mark.parametrize("redfish_password", ["calvin"])
    @pytest.mark.parametrize("masters_count", [3])
    @pytest.mark.parametrize("workers_count", [3])
    @pytest.mark.baremetal_sanity
    def test_baremetal_rac_deployment(
            self,
            cluster,
            record_property,
            redfish_machines,
            redfish_user,
            redfish_password,
            redfish_enabled,
            masters_count,
            workers_count,
    ):
        record_property("polarion-testcase-id", "OCP-32378")
        cluster.generate_and_download_infra_env()
        # NFS mount - > current running machine
        cluster.nodes.controller.set_nfs_mount_path(
            self.nfs_servers(), cluster._infra_env._config.iso_download_path
        )
        # Adapter will add support for list disks ,ip's for ssh node based on cluster inventory
        cluster.nodes.controller.set_adapter_controller(cluster)
        cluster.nodes.prepare_nodes()
        cluster.wait_until_hosts_are_discovered(allow_insufficient=True)
        self._clean_disks(cluster)
        self._set_roles_names(cluster, masters_count)
        self._set_bundle_operators(cluster)
        self._set_installation_disk(cluster)
        # Get ocp network.
        node_ip = cluster.nodes.controller.get_node_ips_and_macs("master-0")[0][0]
        api_vip, ingress = self._get_vip_ingress(node_ip)
        api_vips = [{"ip": str(api_vip)}]
        ingress_vips = [{"ip": str(ingress)}]

        # Change the vips to primary OCP network  - validation success.
        cluster.set_advanced_networking(api_vips=api_vips, ingress_vips=ingress_vips)
        cluster.wait_for_ready_to_install()
        # Example for ssh to a node and run command
        # nodes = cluster.nodes.get_nodes()
        # name = nodes[0].name
        # logging.info(f"Node name is {name}")
        # nodes[0].run_command("lsblk")
        cluster.start_install_and_wait_for_installed()
