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



class DataVolume:
    def __init__(self):
        self.data_volume_name = None
        self.image_url = None
        self.storage_class = None


class DataVolumeBuilder(TemplateBuilder):
    def build(self, data_volume_name,
              image_url="http://download.eng.rdu.redhat.com/released/rhel-8/RHEL-8/8.10.0/BaseOS/x86_64/images/"
                        "rhel-guest-image-8.10-1362.x86_64.qcow2", storage_class="ocs-storagecluster-ceph-rbd"):
        self.template.data_volume_name = data_volume_name
        self.template.image_url = image_url
        self.template.storage_class = storage_class