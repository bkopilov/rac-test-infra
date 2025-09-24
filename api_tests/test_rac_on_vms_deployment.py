import logging
from tests.base_test import BaseTest
from tests.config import global_variables

from api_tests.common.hammer_db import hammer_builder
from api_tests.common.waiters import (wait_for_operators_status_ready,
                                      wait_for_cnv_status_available, wait_for_odf_status_ready)

from api_tests.common.libivrt_network import RacNetworkBuilder, RacNetwork
from api_tests.common.ocp_network import NodeNetworkConfigurationPolicy, NetworkAttachmentDefinition
from api_tests.common.ocp_network import NetworkAttachmentDefinitionBuilder, NodeNetworkConfigurationPolicyBuilder
from api_tests.common.ocp_storage import PersistentVolumeClaimBuilder, PersistentVolumeClaim
from api_tests.common.ocp_virtual_machine import VirtualMachineBuilder, VirtualMachine
from api_tests.common.builder_template import generate_builder, TemplateDirector
from api_tests.common.libivrt_network import RacInterfaceBuilder, RacInterface
from api_tests.common.commands.oc_commands import oc_create, oc_node_interfaces_ip
from api_tests.common.commands.shell_commands import run_shell_command
from api_tests.common.commands.node_commands import NodeSshHandler
from api_tests.common.oracle21c_rac.rac_builder import Builder21cRac, RacDirector
from api_tests.common.hammer_db.hammer_builder import Hammer5Builder
from api_tests.common.utils import generate_mac
from netaddr import IPNetwork

import copy
import libvirt
import pytest
import time
logger = logging.getLogger(__name__)

CPU_CORES = 70
RAM_MEMORY_GIB = 1024 * 70
DISK_COUNT = 2
VIRTUALIZATION_BUNDLE = ['odf', 'cnv', 'lso', 'nmstate']
APPLY_ACTION_TIMEOUT = 10
APPLY_VM_TIMEOUT = 60 * 3


class TestRacDeployment(BaseTest):
    """Test RAC oracle on OCPv with 2 vms conntected to shared backend.
    The test creates a cluster with 3 masters nodes, enable virtualization.
    The RAC topology post installation requires 2 OCPv vms.

    ----------- public network -----------
            |                 |
         NODE A             NODE B
           |                   |
    ----------- private network -----------
                     |    Connected via ODF (cepth) or iSCSI backend(netapp)
                [ ]  [ ]  [ ]
                SHARED VOLUMES

    The test will run on hypervisor runnning libvirt
    ---------------------Hypervisor --------------------
    |             open-shift cluster
          Master0        Master1          Master2
    |        |             | vth               |
    |      ----------- br-ex bridge ----------
    |                      |
    |                    ens3
    |
          Inside cluster nodes (libvirt vms) we run ocpv vms)
    ----------------------------------------------------

    In order to allow connection from outside to ocpV nodes we add additional interfaces on libvirt,
    connected to the hypervisor and the other side will be connected to libvirt nodes interfaces, OCPv
    nodes will be connected to the libvirt masters via bridge.

    DHCP / DNS allocation will be provided by libvirt to the OCPV nodes. they all chained by bridge
    Hypervisor <-> bridge <-->  Master eth <---> <--bridge--> <----> OCPv vm


    Once the cluster installed we will have 3 masters inside the hypervisor.
    We will allow to run python oc commands from the hypervisor and ssh to ocpv vms


    """
    # Creating two VM's each one will have the reserved mac for "permanent" address for each interface
    RAC_NETWORKS = [{"name": "test-infra-rac1", "cidr": IPNetwork("192.168.120.0/24"), "macs": [generate_mac(), generate_mac()]},
                    {"name": "test-infra-rac2", "cidr": IPNetwork("192.168.121.0/24"), "macs": [generate_mac(), generate_mac()]},
                    {"name": "test-infra-rac3", "cidr": IPNetwork("192.168.122.0/24"), "macs": [generate_mac(), generate_mac()]}]

    # RAC DNS and DHCP from libvirt configuration external
    RAC_DNS = {"vip1": {"dns": "oralab1-vip", "ip": "192.168.120.201"},
               "vip2": {"dns": "oralab2-vip", "ip": "192.168.120.202"},
               "scan": {"dns": "oralab-scan", "ip": ["192.168.120.69", "192.168.120.70", "192.168.120.71"]},
               "node1": {"dns": "oralab1", "ip": "192.168.121.101"},
               "node2": {"dns": "oralab2", "ip": "192.168.121.102"},
               "domain": "oracle-rac.openinfra.lab"
               }


    @staticmethod
    def _set_bundle_operators(cluster, *operators):
        # Create operators bundle , remove duplicate
        operators_list = copy.deepcopy(VIRTUALIZATION_BUNDLE)
        operators_list.extend(operators)
        for operator in set(operators_list):
            cluster.set_olm_operator(operator)

    @pytest.fixture
    def cluster_networks(self, cluster):
        rac_networks = []  # used for cleanup
        for network in self.RAC_NETWORKS:
            rac_builder = RacNetworkBuilder(RacNetwork())
            rac_builder.build_bridge_network(bridge_name=network['name'], bridge_mac=generate_mac(),
                                             domain_name=self.RAC_DNS['domain'],
                                             bridge_ipv4=str(network['cidr'].ip + 1),
                                             bridge_ipv4_subnet="24")

            rac_builder.build_rac_vip_network(vip1_ipv4=self.RAC_DNS['vip1']["ip"],
                                              vip1_host=f"{self.RAC_DNS['vip1']["dns"]}.{self.RAC_DNS['domain']}",
                                              vip2_ipv4=self.RAC_DNS['vip2']["ip"],
                                              vip2_host=f"{self.RAC_DNS['vip2']["dns"]}.{self.RAC_DNS['domain']}")

            rac_builder.build_rac_scan_network(scan1_ipv4=self.RAC_DNS['scan']['ip'][0],
                                               scan2_ipv4=self.RAC_DNS['scan']['ip'][1],
                                               scan3_ipv4=self.RAC_DNS['scan']['ip'][2],
                                               scan_host=f"{self.RAC_DNS['scan']['dns']}.{self.RAC_DNS['domain']}")
            # Need to save the MACs for later when creating interfaces on OCPv , ip allocation per MAC
            rac1_mac = network['macs'][0]
            rac2_mac = network['macs'][1]
            rac_builder.build_rac_dhcp(bridge_dhcp_start_ipv4=str(network['cidr'].ip + 2),
                                       bridge_dhcp_end_ipv4=str(network['cidr'].ip + 32),
                                       rac1_mac=rac1_mac, rac1_hostname=self.RAC_DNS['node1']['dns'],
                                       rac1_ipv4=str(network['cidr'].ip + 101),
                                       rac2_mac=rac2_mac, rac2_hostname=self.RAC_DNS['node2']['dns'],
                                       rac2_ipv4=str(network['cidr'].ip + 102))

            director = TemplateDirector(template_builder=rac_builder)
            params = director.j2_params()
            output = generate_builder("rac_network.j2", package_path="templates/libvirt",  **params)
            net = cluster.nodes.controller.libvirt_connection.networkDefineXML(output)
            rac_networks.append(net)
            net.setAutostart(1)
            net.create()
            cluster.nodes.controller.rac_networks = rac_networks

        yield cluster
        # Cleanup phase , remove additional network created when not attached.
        if not global_variables.test_teardown:
            return

        for clean_network in rac_networks:
            try:
                logger.info(f"Cleaning up networks {str(clean_network)}")
                clean_network.destroy()
                clean_network.undefine()
            except Exception as e:
                logger.error(e)

    def _attach_interface_to_nodes(self, cluster):
        """Attach interface to nodes masters when node in shutdown mode
        The mac address is not important here because we need reservation to rac OCPv
        :param cluster:
        :return:
        """

        attach_flags = libvirt.VIR_DOMAIN_AFFECT_CONFIG
        for master in cluster.nodes.get_masters():
            for network in self.RAC_NETWORKS:
                node_obj = cluster.nodes.controller.libvirt_connection.lookupByName(master.name)
                rac_interface = RacInterface()
                rac_builder = RacInterfaceBuilder(rac_interface)
                rac_builder.attach_interface(mac_address=generate_mac(), network_name=network['name'])
                director = TemplateDirector(template_builder=rac_builder)
                params = director.j2_params()
                output = generate_builder("rac_interface.j2", package_path="templates/libvirt", **params)
                node_obj.attachDeviceFlags(output, attach_flags)
                time.sleep(APPLY_ACTION_TIMEOUT)

    def _install_cluster(self, cluster):
        cluster.generate_and_download_infra_env()
        cluster.nodes.prepare_nodes()
        self._set_bundle_operators(cluster)
        self._attach_interface_to_nodes(cluster)
        cluster.nodes.start_all()
        cluster.wait_until_hosts_are_discovered()
        cluster.set_host_roles()
        cluster.set_network_params()
        cluster.wait_for_ready_to_install()
        cluster.start_install_and_wait_for_installed()
        # When cluster installed successfully - /tmp/kubeconfig inside the test-infra container access
        # Update /etc/hosts file to allow access to cluster from container
        self.update_oc_config(cluster.nodes, cluster)

    def _build_ocpv_network_policy(self):
        """Create network policy contains bridge name and mapped port to it
        The assigned port is from the worker side and another port will be VM.

        ens12(Worker) <--> |Bridge RAC1|  --- (eth0) <VM ocp>
             |
        | Bridge |(br-ex )
             |
        ens3(Hypervisor libvirt )  --> runs dhcp and dns for RAC
             |
           External
        """

        def get_interface_name(cidr):
            node_interfaces = oc_node_interfaces_ip()
            for node_interface in node_interfaces:
                if node_interface['ipv4']:
                    if IPNetwork(node_interface['ipv4']).cidr == cidr:
                        return node_interface['name']
            raise RuntimeError("Unable to find interface for cidr")

        for network in self.RAC_NETWORKS:
            interface_name = get_interface_name(network['cidr'])
            network_policy_builder = NodeNetworkConfigurationPolicyBuilder(NodeNetworkConfigurationPolicy())
            network_policy_builder.build(bridge_name=network['name'], bridge_port=interface_name)
            director = TemplateDirector(template_builder=network_policy_builder)
            params = director.j2_params()
            output = generate_builder("NodeNetworkConfigurationPolicy.j2", package_path="templates/ocp", **params)
            oc_create(str_dict=output, namespace="default")
            time.sleep(APPLY_ACTION_TIMEOUT)

    def _build_ocpv_network_attachment(self):
        # Add network attachments definitions - contains the bridge name mapped to port, used by virtual machines
        for net in self.RAC_NETWORKS:
            network_attachment_builder = NetworkAttachmentDefinitionBuilder(NetworkAttachmentDefinition())
            network_attachment_builder.build(net['name'])
            director = TemplateDirector(template_builder=network_attachment_builder)
            params = director.j2_params()
            output = generate_builder("NetworkAttachmentDefinition.j2", package_path="templates/ocp", **params)
            oc_create(str_dict=output, namespace="default")
            time.sleep(APPLY_ACTION_TIMEOUT)

    def _build_ocpv_storage_pvc(self):
        # RAC will run with 3 shared volumes volume names shared-volume1 , shared-volume2, shared-volume3
        for index in range(1, 4):
            pvc_builder = PersistentVolumeClaimBuilder(PersistentVolumeClaim())
            pvc_builder.build(pvc_name="volume" + str(index), pvc_access_permissions="ReadWriteMany",
                              pvc_size="20Gi", pvc_storage_class="ocs-storagecluster-ceph-rbd-virtualization",
                              pvc_mode="Block")
            director = TemplateDirector(template_builder=pvc_builder)
            params = director.j2_params()
            output = generate_builder("PersistentVolumeClaim.j2", package_path="templates/ocp", **params)
            oc_create(str_dict=output, namespace="default")
            time.sleep(APPLY_ACTION_TIMEOUT)

    def _build_ocpv_vms(self):
        """Create 2 VMs inside OCP with 3 nics for rac accessible from hypervisor"""
        for index in range(2):
            vm_builder = VirtualMachineBuilder(VirtualMachine())
            vm_builder.build_storage(node_name="oralab" + str(index + 1), ssh_key_name="ssh-key",
                                     volume1="volume" + str(1),
                                     volume2="volume" + str(2),
                                     volume3="volume" + str(3),
                                     disk_bus="scsi")

            vm_builder.build_network(interface_name1=self.RAC_NETWORKS[0]['name'],
                                     interface_name2=self.RAC_NETWORKS[1]['name'],
                                     interface_name3=self.RAC_NETWORKS[2]['name'],
                                     mac_address1=self.RAC_NETWORKS[0]['macs'][index],
                                     mac_address2=self.RAC_NETWORKS[1]['macs'][index],
                                     mac_address3=self.RAC_NETWORKS[2]['macs'][index])
            director = TemplateDirector(template_builder=vm_builder)
            params = director.j2_params()
            output = generate_builder("VirtualMachine.j2", package_path="templates/ocp", **params)
            oc_create(str_dict=output, namespace="default")
            time.sleep(APPLY_VM_TIMEOUT)

    def _build_rac_cluster(self):
        # Created dummy web server on running hypervisr to download binaries
        rac_builder = Builder21cRac(download_binaries=["http://10.9.76.8:8888/LINUX.X64_213000_grid_home.zip",
                                                       "http://10.9.76.8:8888/LINUX.X64_213000_db_home.zip"])
        user = "cloud-user"
        private_key = "/root/.ssh/id_rsa"
        ssh_handlers = [NodeSshHandler(ipv4_address=self.RAC_DNS['node1']['ip'], username=user,
                                       hostname=self.RAC_DNS['node1']['dns'], private_ssh_key_path=private_key),
                        NodeSshHandler(ipv4_address=self.RAC_DNS['node2']['ip'], username=user,
                                       hostname=self.RAC_DNS['node2']['dns'], private_ssh_key_path=private_key)]
        rac_director = RacDirector(rac_builder=rac_builder, ssh_handlers=ssh_handlers)
        rac_director.build()

    def _build_hammer_db(self):
        hammer_handler = run_shell_command
        hammerdb = Hammer5Builder(hammer_handler)
        hammerdb.build_dnf_package()
        # copy template files:
        build_content = generate_builder("build.tcl", package_path="templates/hammer_db")
        hammerdb.write_to_file("/opt/HammerDB-5.0/build.tcl", build_content)

        run_content = generate_builder("run.tcl", package_path="templates/hammer_db")
        hammerdb.write_to_file("/opt/HammerDB-5.0/run.tcl", run_content)

        drop_content = generate_builder("drop_tpcc_user.sh", package_path="templates/hammer_db")
        hammerdb.write_to_file("/opt/HammerDB-5.0/drop_tpcc_user.sh", drop_content)

        profile_content = generate_builder("profile.sh", package_path="templates/hammer_db")
        hammerdb.write_to_file("/opt/HammerDB-5.0/profile.sh", profile_content)
        
        hammerdb.build_etc_hosts()
        hammerdb.build_tns_names()
        hammerdb.hammerdbcli_build()
        hammerdb.hammerdbcli_run()
        hammerdb.build_restore_hosts()


    @pytest.mark.rac
    @pytest.mark.parametrize("masters_count", [3])
    @pytest.mark.parametrize("workers_count", [0])
    @pytest.mark.parametrize("master_vcpu", [CPU_CORES])
    @pytest.mark.parametrize("master_memory", [RAM_MEMORY_GIB])
    @pytest.mark.parametrize("master_disk_count", [DISK_COUNT])
    def test_create_rac_deployment(self, cluster_networks, masters_count, workers_count, master_vcpu, master_memory,
                                   master_disk_count):
        self._install_cluster(cluster_networks)
        wait_for_operators_status_ready()
        wait_for_cnv_status_available()
        wait_for_odf_status_ready()
        time.sleep(APPLY_ACTION_TIMEOUT)
        self._build_ocpv_network_policy()
        self._build_ocpv_network_attachment()
        self._build_ocpv_storage_pvc()
        # allow ssh from running test-infra hypervisor to the RAC nodes
        run_shell_command(cmd="oc create secret generic ssh-key --from-file=ssh-privatekey=/root/.ssh/id_rsa "
                              "--from-file=ssh-publickey=/root/.ssh/id_rsa.pub")
        self._build_ocpv_vms()
        # rac installation on VMs.
        run_shell_command("cp /dev/null /root/.ssh/known_hosts")
        self._build_rac_cluster()
        self._build_hammer_db()
        logging.info(f"kubeconfig path:{cluster_networks._config.kubeconfig_path}")
        logging.info(f"cluster api and id: {str(cluster_networks.get_details().api_vips)}")
        logging.info(f"cluster web ui credentials: "
                     f"{str(cluster_networks.api_client.get_cluster_admin_credentials(cluster_networks.id))}")



