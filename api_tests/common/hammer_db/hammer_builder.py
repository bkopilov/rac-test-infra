from api_tests.common.hammer_db.package_installation import PackageInstallHammer5
from api_tests.common.hammer_db.hosts_file import HostFileSetting
from api_tests.common.hammer_db.tns_names import TnsNamesOracle
from api_tests.common.hammer_db.buid_run import BuildRunHammerDB


class HammerBuilder:
    pass

INSTALLATION_TIMEOUT = 60 * 35

class HammerParserResult:

    @classmethod
    def parse_tpm_average(cls, res_string):
        if not res_string:
            return -1
        else:
            # Expecting for '948 Oracle tpm' messages
            res_numbers = [int(b.split()[0]) for b in res_string.splitlines() if "Oracle tpm" in b]
            return sum(res_numbers) / len(res_numbers)




class Hammer5Builder(HammerBuilder):

    TPM_AVERAGE = 450

    def __init__(self, cmd_handler):
        self.packages = PackageInstallHammer5
        self.host_file = HostFileSetting
        self.tns_names = TnsNamesOracle
        self.build_run = BuildRunHammerDB
        self.cmd_handler = cmd_handler

    def build_dnf_package(self):
        remove_folder = self.packages.remove_old_packages()
        dnf_install = self.packages.package_pre_install()
        self.cmd_handler(remove_folder)
        self.cmd_handler(dnf_install)

    def build_etc_hosts(self):
        save_host = self.host_file.save_hosts_file()
        hosts_file = self.host_file.set_hosts_file()
        self.cmd_handler(save_host)
        self.cmd_handler(hosts_file)

    def build_restore_hosts(self):
        restore_host = self.host_file.restore_hosts_file()
        self.cmd_handler(restore_host)

    def build_tns_names(self):
        tns_install = self.tns_names.tns_name_configuration()
        self.cmd_handler(tns_install)

    def  hammerdbcli_build(self):
        build_cmd = self.build_run.build_hammerbd()
        env_param = self.build_run.env_params()
        self.cmd_handler(env_param)
        self.cmd_handler(build_cmd)

    def  hammerdbcli_run(self):
        build_cmd = self.build_run.run_hammerbd()
        output = self.cmd_handler(build_cmd)
        return HammerParserResult.parse_tpm_average(output)

    def hammerdbcli_drop(self):
        build_cmd = self.build_run.drop_hammerbd()
        self.cmd_handler(build_cmd)

    def write_to_file(self, file_path, content):
        with open(file_path, "a") as file:
            for c in content.split("\n"):
                file.write(c + "\n")

        self.cmd_handler(f"""bash -c "chmod 777 {file_path}" """)
