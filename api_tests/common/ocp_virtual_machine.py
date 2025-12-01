import logging

from .builder_template import TemplateBuilder
logger = logging.getLogger(__name__)


class VirtualMachine:
    def __init__(self):
        self.node_name = None
        self.data_volume_image = None
        self.ssh_key_name = None
        self.volume1 = None
        self.volume2 = None
        self.volume3 = None
        self.disk_bus = None
        self.interface_name1 = None
        self.interface_name2 = None
        self.interface_name3 = None
        self.mac_address1 = None
        self.mac_address2 = None
        self.mac_address3 = None


class VirtualMachineBuilder(TemplateBuilder):
    """Update VirtualMachine product params"""
    def build_storage(self, node_name, data_volume_image, ssh_key_name, volume1, volume2, volume3, disk_bus="scsi"):
        self.template.node_name = node_name
        self.template.data_volume_image = data_volume_image
        self.template.ssh_key_name = ssh_key_name
        self.template.volume1 = volume1
        self.template.volume2 = volume2
        self.template.volume3 = volume3
        self.template.disk_bus = disk_bus

    def build_network(self, interface_name1, interface_name2, interface_name3,
                      mac_address1, mac_address2, mac_address3):
        self.template.interface_name1 = interface_name1
        self.template.interface_name2 = interface_name2
        self.template.interface_name3 = interface_name3
        self.template.mac_address1 = mac_address1
        self.template.mac_address2 = mac_address2
        self.template.mac_address3 = mac_address3

    def build_thread_io(self, enabled_thread_io, thread_count):
        self.template.enabled_thread_io = enabled_thread_io
        self.template.thread_count = thread_count



