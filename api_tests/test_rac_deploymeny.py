import logging
from tests.base_test import BaseTest
from api_tests.common.libivrt_network import RacNetworkBuilder, generate_xml_network, RacNetwork
from api_tests.common.libivrt_network import RacInterfaceBuilder, RacNetworkDirector, RacInterface
from netaddr import IPNetwork

import copy
import libvirt
import random
import pytest

logger = logging.getLogger(__name__)

CPU_CORES = 60
RAM_MEMORY_GIB = 1024 * 60
DISK_COUNT = 2
VIRTUALIZATION_BUNDLE = ['odf', 'cnv', 'self-node-remediation', 'lso', 'nmstate', 'kube-descheduler',
                         'node-healthcheck', 'fence-agents-remediation', 'node-maintenance']


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
    |             open-shfit cluster
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

    RAC_MACS = {}
    RAC_NETWORKS = ["rac1", "rac2", "rac3"]

    @staticmethod
    def _set_bundle_operators(cluster, *operators):
        # Create operators bundle , remove duplicate
        operators_list = copy.deepcopy(VIRTUALIZATION_BUNDLE)
        operators_list.extend(operators)
        for operator in set(operators_list):
            cluster.set_olm_operator(operator)

    @staticmethod
    def generate_mac():
        return "fe:54:00:" + ":".join([('0'+hex(random.randint(0, 100))[2:])[-2:].upper() for _ in range(3)])

    @pytest.fixture
    def clusters_network(self, cluster):
        rac_networks = []  # used for cleanup
        ipv4_net = IPNetwork("192.168.120.0").ip
        rac_net = IPNetwork("192.168.120.0").ip  # same for all dns server - rac scan and vip
        jump_network = 256
        for net_name in self.RAC_NETWORKS:
            rac_network = RacNetwork()
            rac_builder = RacNetworkBuilder(rac_network)
            rac_builder.build_bridge_network(bridge_name=net_name, bridge_mac=self.generate_mac(),
                                             domain_name="oracle-rac.openinfra.lab", bridge_ipv4=str(ipv4_net + 1),
                                             bridge_ipv4_subnet="24")

            rac_builder.build_rac_vip_network(vip1_ipv4=str(rac_net + 201),
                                              vip1_host="oralab1-vip.oracle-rac.openinfra.lab",
                                              vip2_ipv4=str(rac_net + 202),
                                              vip2_host="oralab2-vip.oracle-rac.openinfra.lab")

            rac_builder.build_rac_scan_network(scan1_ipv4=str(rac_net + 69), scan2_ipv4=str(rac_net + 70),
                                               scan3_ipv4=str(rac_net + 71),
                                               scan_host="oralab-scan.oracle-rac.openinfra.lab")
            # Need to save the MACs for later when creating interfaces on OCPv , ip allocation per MAC
            rac1_mac = self.generate_mac()
            rac2_mac = self.generate_mac()
            rac_builder.build_rac_dhcp(bridge_dhcp_start_ipv4=str(ipv4_net + 2),
                                       bridge_dhcp_end_ipv4=str(ipv4_net + 32),
                                       rac1_mac=rac1_mac, rac1_hostname="oralab1", rac1_ipv4=str(ipv4_net + 101),
                                       rac2_mac=rac2_mac, rac2_hostname="oralab2", rac2_ipv4=str(ipv4_net + 102))

            self.RAC_MACS[net_name] = [rac1_mac, rac2_mac]
            director = RacNetworkDirector(network_builder=rac_builder)
            params = director.j2_params()
            output = generate_xml_network("rac_network.j2", **params)
            net = cluster.nodes.controller.libvirt_connection.networkDefineXML(output)
            rac_networks.append(net)
            net.setAutostart(1)
            net.create()
            cluster.nodes.controller.rac_networks = rac_networks
            ipv4_net += jump_network

        yield cluster
        # cleanup phase , remove additional network created when not attached.
        for net in rac_networks:
            try:
                net.destroy()
                net.undefine()
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
            for net_name in self.RAC_NETWORKS:
                node_obj = cluster.nodes.controller.libvirt_connection.lookupByName(master.name)
                rac_interface = RacInterface()
                rac_builder = RacInterfaceBuilder(rac_interface)
                rac_builder.attach_interface(mac_address=self.generate_mac(), network_name=net_name)
                director = RacNetworkDirector(network_builder=rac_builder)
                params = director.j2_params()
                output = generate_xml_network("rac_interface.j2", **params)
                node_obj.attachDeviceFlags(output, attach_flags)

    @pytest.mark.rac
    @pytest.mark.parametrize("masters_count", [3])
    @pytest.mark.parametrize("workers_count", [0])
    @pytest.mark.parametrize("master_vcpu", [CPU_CORES])
    @pytest.mark.parametrize("master_memory", [RAM_MEMORY_GIB])
    @pytest.mark.parametrize("master_disk_count", [DISK_COUNT])
    def test_create_rac_deployment(self, clusters_network, masters_count, workers_count, master_vcpu, master_memory,
                                   master_disk_count):
        cluster = clusters_network
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

