import logging
from .builder_template import TemplateBuilder
logger = logging.getLogger(__name__)


class PersistentVolumeClaim:
    def __init__(self):
        self.pvc_name = None
        self.pvc_access_permissions = None
        self.pvc_size = None
        self.pvc_storage_class = None
        self.pvc_mode = None


class PersistentVolumeClaimBuilder(TemplateBuilder):
    """Update NodeNetworkConfigurationPolicy product params"""
    def build(self, pvc_name, pvc_access_permissions, pvc_size, pvc_storage_class, pvc_mode):
        self.template.pvc_name = pvc_name
        self.template.pvc_access_permissions = pvc_access_permissions
        self.template.pvc_size = pvc_size
        self.template.pvc_storage_class = pvc_storage_class
        self.template.pvc_mode = pvc_mode



