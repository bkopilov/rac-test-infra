import consts
import scp
import time
import logging
from assisted_test_infra.test_infra.controllers.node_controllers.ssh import SshConnection

import paramiko

from datetime import datetime

logger = logging.getLogger(__name__)


class NodeSshHandler(SshConnection):
    def __init__(self, ipv4_address, username, hostname, private_ssh_key_path=None, password=None, port=22):
        super().__init__(ip=ipv4_address, private_ssh_key_path=private_ssh_key_path, username=username, port=port)
        self._ssh_client = None
        self.password = password
        self.hostname = hostname

    @property
    def ssh_ipv4(self):
        return self._ip

    def execute(self, command, timeout=60 * 35, ignore_errors=False, post_command_wait=0):
        logging.info(f'\n {datetime.now()}|{self.ssh_ipv4}|>>>\n{command}\n---')
        output = None
        try:
            output = self._execute(command, timeout)
            time.sleep(post_command_wait)
            logging.info(f'\n{datetime.now()}|{self.ssh_ipv4}|<<<\n{output}\n---\n')
            return output
        except Exception as e:
            if ignore_errors:
                logging.info(f'\n{datetime.now()}|{self.ssh_ipv4}|<<<\n{output}\n---\n')
                return output
            raise e

    def _execute(self, command, timeout=60):
        if not self._ssh_client:
            self.connect()

        stdin, stdout, stderr = self._ssh_client.exec_command(command, timeout=timeout)
        output = stdout.read()
        error = stderr.read()
        status = stdout.channel.recv_exit_status()

        output = output.decode('utf-8', errors='ignore')
        if status != 0:
            e = RuntimeError(
                f"{datetime.now()}|Failed executing, status '{status}', output was:\n{output} stderr \n"
                f"{error.decode('utf-8', errors='ignore')}"
            )
            e.output = output
            raise e
        return output

    def upload_file(self, local_source_path, remote_target_path):
        super().upload_file(local_source_path, remote_target_path)

    def download_file(self, remote_source_path, local_target_path):
        super().download_file(remote_source_path, local_target_path)

    def wait_for_tcp_server(self, timeout=120, interval=5):
        logging.info(f"{self} -> Wait for %s to be available", self._ip)
        before = time.time()
        while time.time() - before < timeout:
            if self._raw_tcp_connect((self._ip, self._port)):
                return
            time.sleep(interval)
        raise TimeoutError(
            "SSH TCP Server '[%(hostname)s]:%(port)s' did not respond within timeout"
            % dict(hostname=self._ip, port=self._port)
        )

    def connect(self, timeout=180):
        logging.info("Going to connect to ip %s", self._ip)
        self.wait_for_tcp_server(timeout=timeout)
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.known_hosts = None
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not self.password:
            self._ssh_client.connect(
                hostname=self._ip,
                port=self._port,
                username=self._username,
                allow_agent=False,
                timeout=timeout,
                look_for_keys=False,
                auth_timeout=timeout,
                pkey=paramiko.RSAKey.from_private_key_file(self._key_path),
            )
        else:
            self._ssh_client.connect(
                hostname=self._ip,
                port=self._port,
                password=self.password,
                username=self._username,
                allow_agent=False,
                timeout=timeout,
            )

        self._ssh_client.get_transport().set_keepalive(15)

