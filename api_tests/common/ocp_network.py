import logging
from .builder_template import TemplateBuilder
logger = logging.getLogger(__name__)


class NodeNetworkConfigurationPolicy:
    """RacOcpNetwork is the product for template builder"""

    def __init__(self):
        self.bridge_name = None
        self.bridge_port = None


class NodeNetworkConfigurationPolicyBuilder(TemplateBuilder):
    """Update NodeNetworkConfigurationPolicy product params"""
    def build(self, bridge_name, bridge_port):
        self.template.bridge_name = bridge_name
        self.template.bridge_port = bridge_port


class NetworkAttachmentDefinition:
    """NetworkAttachmentDefinition is the product for template builder"""

    def __init__(self):
        self.bridge_name = None


class NetworkAttachmentDefinitionBuilder(TemplateBuilder):
    """Update NodeNetworkConfigurationPolicy product params"""

    def build(self, bridge_name):
        self.template.bridge_name = bridge_name
