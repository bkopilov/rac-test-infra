import logging
from .builder_template import TemplateBuilder
logger = logging.getLogger(__name__)


class RacNetwork:
    """RacNetwork is the product for template builder"""

    def __init__(self):
        self.bridge_name = None
        self.network_name = None
        self.bridge_mac = None
        self.domain_name = "oracle-rac.openinfra.lab"
        self.vip1_ipv4 = None
        self.vip1_host = "oralab1-vip.oracle-rac.openinfra.lab"
        self.vip2_ipv4 = None
        self.vip2_host = "oralab2-vip.oracle-rac.openinfra.lab"
        self.scan1_ipv4 = None
        self.scan2_ipv4 = None
        self.scan3_ipv4 = None
        self.scan_host = "oralab-scan.oracle-rac.openinfra.lab"
        self.bridge_ipv4 = None
        self.bridge_ipv4_subnet = None
        self.bridge_dhcp_start_ipv4 = None
        self.bridge_dhcp_end_ipv4 = None
        self.rac1_mac = None
        self.rac2_mac = None
        self.rac1_hostname = "oralab1"
        self.rac2_hostname = "oralab2"
        self.rac1_ipv4 = None
        self.rac2_ipv4 = None


class RacInterface:
    """RacInterface is the product for template builder"""

    def __init__(self):
        self.mac_address = None
        self.network_name = None


class RacInterfaceBuilder(TemplateBuilder):
    """Update RacInterface product params"""
    def attach_interface(self, mac_address, network_name):
        self.template.mac_address = mac_address
        self.template.network_name = network_name


class RacNetworkBuilder(TemplateBuilder):
    """Update RacNetwork product params"""

    def build_bridge_network(self, bridge_name, bridge_mac, domain_name, bridge_ipv4, bridge_ipv4_subnet):
        self.template.network_name = bridge_name
        self.template.bridge_name = bridge_name
        self.template.bridge_mac = bridge_mac
        self.template.domain_name = domain_name
        self.template.bridge_ipv4 = bridge_ipv4
        self.template.bridge_ipv4_subnet = bridge_ipv4_subnet

    def build_rac_vip_network(self, vip1_ipv4, vip1_host, vip2_ipv4, vip2_host):
        self.template.vip1_ipv4 = vip1_ipv4
        self.template.vip1_host = vip1_host
        self.template.vip2_ipv4 = vip2_ipv4
        self.template.vip2_host = vip2_host

    def build_rac_scan_network(self, scan1_ipv4, scan2_ipv4, scan3_ipv4, scan_host):
        self.template.scan1_ipv4 = scan1_ipv4
        self.template.scan2_ipv4 = scan2_ipv4
        self.template.scan3_ipv4 = scan3_ipv4
        self.template.scan_host = scan_host

    def build_rac_dhcp(self, bridge_dhcp_start_ipv4, bridge_dhcp_end_ipv4, rac1_mac, rac1_hostname, rac1_ipv4,
                       rac2_mac, rac2_hostname, rac2_ipv4):
        self.template.bridge_dhcp_start_ipv4 = bridge_dhcp_start_ipv4
        self.template.bridge_dhcp_end_ipv4 = bridge_dhcp_end_ipv4
        self.template.rac1_mac = rac1_mac
        self.template.rac1_hostname = rac1_hostname
        self.template.rac1_ipv4 = rac1_ipv4
        self.template.rac2_mac = rac2_mac
        self.template.rac2_hostname = rac2_hostname
        self.template.rac2_ipv4 = rac2_ipv4
