import consts
import logging
from assisted_test_infra.test_infra.controllers.node_controllers.ssh import SshConnection

logger = logging.getLogger(__name__)


class NodeSshHandler(SshConnection):
    def __init__(self, ipv4_address, username, private_ssh_key_path=None, port=22):
        super().__init__(ip=ipv4_address, private_ssh_key_path=private_ssh_key_path, username=username, port=port)

    def execute(self, command, timeout=60, verbose=True):
        return super().execute(command, timeout, verbose)

    def upload_file(self, local_source_path, remote_target_path):
        super().upload_file(local_source_path, remote_target_path)

    def download_file(self, remote_source_path, local_target_path):
        super().download_file(remote_source_path, local_target_path)