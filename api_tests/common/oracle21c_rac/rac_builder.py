import time

from .repo_creation import RepoCreation21cRac
from .users_management import UsersManagement21cRac
from .package_installation import PackageInstallation21cRac
from .binaries_management import Binaries21cRac
from .grid_management import GridManagement21cRac
from .database_management import DataBaseManagement21cRac
from .asm_disks import AsmDisks21cRac

from retry import retry

class RacBuilder:
    pass

INSTALLATION_TIMEOUT = 60 * 40
POST_COMMAND_WAIT = 45
POST_GRID_WAIT = 60
RETRY_TIMES = 3
RETRY_DELAY = 30

class Builder21cRac(RacBuilder):
    def __init__(self, download_binaries, disks=("vdc", "vdd", "vde")):
        self.repo_creation = RepoCreation21cRac
        self.package_installation = PackageInstallation21cRac
        self.user_management = UsersManagement21cRac
        self.binaries_management = Binaries21cRac
        self.grid_management = GridManagement21cRac
        self.data_base_management = DataBaseManagement21cRac
        self.binaries = download_binaries
        self.asm_disks = AsmDisks21cRac
        self.disks = disks

    def create_repo(self, ssh_handlers):
        ssl_verify_cmd = self.repo_creation.create_ssl_verify()
        repo_cmd = self.repo_creation.create_repo()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(ssl_verify_cmd)
            ssh_handler.execute(repo_cmd)

    def create_packages(self, ssh_handlers):
        pre_install_cmd = self.package_installation.package_pre_install()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(pre_install_cmd)

    def create_users(self, ssh_handlers):
        groups_cmd = self.user_management.create_users_group()
        ssh_keys_cmd = self.user_management.create_ssh_keys()
        directories_cmd = self.user_management.create_directories()
        enable_tsc = self.user_management.set_tsc_clock_source()
        services_cmd = self.user_management.enable_services()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(groups_cmd)
            ssh_handler.execute(ssh_keys_cmd)
            ssh_handler.execute(directories_cmd)
            ssh_handler.execute(enable_tsc)
            ssh_handler.execute(services_cmd)
        time.sleep(POST_COMMAND_WAIT)


    def create_swap(self, ssh_handlers):
        swap_cmd = self.user_management.create_swap()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(swap_cmd)

    def huge_pages(self, ssh_handlers):
        huge_pages = self.binaries_management.huge_pages()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(huge_pages)


    def create_authorized_keys(self, ssh_handlers):
        get_public_cmd = self.user_management.get_public_key()
        rsa_public1_cmd = ssh_handlers[0].execute(get_public_cmd)
        rsa_public2_cmd = ssh_handlers[1].execute(get_public_cmd)
        update_public1 = self.user_management.update_authorized_key(rsa_public1_cmd)
        update_public2 = self.user_management.update_authorized_key(rsa_public2_cmd)

        ssh_handlers[0].execute(update_public2)
        ssh_handlers[1].execute(update_public1)

        cmd_strict_check = self.user_management.ssh_strict_host_checking()
        ssh_handlers[0].execute(cmd_strict_check)
        ssh_handlers[1].execute(cmd_strict_check)

    def create_no_zero_conf(self, ssh_handlers):
        cmd = self.user_management.no_zero_conf()
        ssh_handlers[0].execute(cmd)
        ssh_handlers[1].execute(cmd)

    def create_ssh_known_hosts(self, ssh_handlers):
        key_scan1_cmd = self.user_management.ssh_key_scans(ssh_handlers[0].ssh_ipv4, ssh_handlers[0].hostname)
        key_scan2_cmd = self.user_management.ssh_key_scans(ssh_handlers[1].ssh_ipv4, ssh_handlers[1].hostname)
        ssh_handlers[0].execute(key_scan2_cmd)
        ssh_handlers[1].execute(key_scan1_cmd)

    def download_binaries(self, ssh_handler):
        for bin_download in self.binaries:
            cmd = self.binaries_management.download_binaries(bin_download)
            ssh_handler.execute(cmd)

    def unzip_grid(self, ssh_handler):
        cmd = self.binaries_management.unzip_grid_binary(self.binaries[0])
        ssh_handler.execute(cmd)

    def unzip_database(self, ssh_handler):
        create_dir = self.binaries_management.create_database_dir()
        unzip = self.binaries_management.unzip_database_binary(self.binaries[1])
        ssh_handler.execute(create_dir)
        ssh_handler.execute(unzip)

    def install_qdisk(self, ssh_handlers):
        cmd = self.binaries_management.copy_qdisk()
        ssh_handlers[0].execute(cmd)
        install1 = self.binaries_management.install_qdisk("/u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm")
        ssh_handlers[0].execute(install1)
        install2 = self.binaries_management.install_qdisk("/tmp/cvuqdisk-1.0.10-1.rpm")
        ssh_handlers[1].execute(install2)

    def install_grid_perinstall(self, ssh_handler):
        cmd = self.grid_management.validate_grid_preinstall()
        try:
            ssh_handler.execute(cmd, post_command_wait=POST_GRID_WAIT)
        except Exception as e:
            print(e)

    #@retry(exceptions=RuntimeError, tries=RETRY_TIMES, delay=RETRY_DELAY)
    def install_grid_phase1(self, ssh_handler, **params):
        cmd = self.grid_management.grid_install_phase1(**params)
        ssh_handler.execute(cmd, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_GRID_WAIT)

    def install_grid_phase2(self, ssh_handlers):
        cmd1 = self.grid_management.grid_install_phase2_1()
        cmd2 = self.grid_management.grid_install_phase2_2()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(cmd1, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_GRID_WAIT)
            ssh_handler.execute(cmd2, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_GRID_WAIT)

    #@retry(exceptions=RuntimeError, tries=RETRY_TIMES, delay=RETRY_DELAY)
    def install_grid_phase3(self, ssh_handler, **params):
        cmd = self.grid_management.grid_install_phase3(**params)
        ssh_handler.execute(cmd, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)

    def create_database_groups(self, ssh_handler):
        cmd_data = self.data_base_management.create_data_disk_group()
        cmd_recovery = self.data_base_management.create_recovery_disk_group()
        ssh_handler.execute(cmd_data, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)
        ssh_handler.execute(cmd_recovery, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)

    def verify_grid_status(self, ssh_handler):
        cmd_grid = self.grid_management.grid_crsctl_stat()
        cmd_disk_group = self.grid_management.grid_disk_group_stat()
        ssh_handler.execute(cmd_grid)
        ssh_handler.execute(cmd_disk_group)

    def create_partitions(self, ssh_handler):
        # create disk partition on node1 - shared disks
        for disk in self.disks:
            cmd = self.asm_disks.create_disk_partition(disk)
            ssh_handler.execute(cmd)

    def create_asm_disks(self, ssh_handlers):
        for ssh_handler in ssh_handlers:
            disks_asm = []
            for disk in self.disks:
                disk_id_cmd = self.asm_disks.disk_id(disk)
                disk_id = ssh_handler.execute(disk_id_cmd)
                if disk_id:
                    # for virtio returns "virtio-volume1"
                    disk_id_remove_bus = disk_id.strip().split("-")[1]
                    disks_asm.append(disk_id_remove_bus)
            assert len(disks_asm) == 3
            user_rules_cmd = self.asm_disks.create_udev(disks_asm[0], disks_asm[1], disks_asm[2])
            ssh_handler.execute(user_rules_cmd)
            reload_rules_cmd = self.asm_disks.reload_udev_rules()
            ssh_handler.execute(reload_rules_cmd)

    def sync_disk(self, ssh_handlers):
        cmd = self.asm_disks.sync_disks()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(cmd, post_command_wait=POST_GRID_WAIT)

    def install_database_phase1(self, ssh_handler):
        # copy_listener_ora = self.data_base_management.copy_listener_ora()
        # ssh_handler.execute(copy_listener_ora, timeout=INSTALLATION_TIMEOUT)

        cmd = self.data_base_management.install_database_phase1()
        ssh_handler.execute(cmd, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)

    def install_database_phase2(self, ssh_handlers):
        cmd = self.data_base_management.install_database_phase2()
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(cmd, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)

    def install_database_phase3(self, ssh_handler):
        cmd = self.data_base_management.install_database_phase3()
        ssh_handler.execute(cmd, timeout=INSTALLATION_TIMEOUT, post_command_wait=POST_COMMAND_WAIT)


class RacDirector:
    def __init__(self, rac_builder, ssh_handlers):
        self.ssh_handlers = ssh_handlers
        self.rac_builder = rac_builder

    def build(self):
        self.rac_builder.create_repo(self.ssh_handlers)
        self.rac_builder.create_packages(self.ssh_handlers)
        self.rac_builder.create_users(self.ssh_handlers)
        self.rac_builder.create_authorized_keys(self.ssh_handlers)
        self.rac_builder.create_no_zero_conf(self.ssh_handlers)
        self.rac_builder.create_ssh_known_hosts(self.ssh_handlers)
        self.rac_builder.huge_pages(self.ssh_handlers)
        self.rac_builder.download_binaries(self.ssh_handlers[0])
        self.rac_builder.unzip_grid(self.ssh_handlers[0])
        self.rac_builder.install_qdisk(self.ssh_handlers)
        self.rac_builder.create_swap(self.ssh_handlers)
        self.rac_builder.install_grid_perinstall(self.ssh_handlers[0])
        self.rac_builder.create_partitions(self.ssh_handlers[0])
        self.rac_builder.sync_disk(self.ssh_handlers)
        self.rac_builder.create_asm_disks(self.ssh_handlers)
        self.rac_builder.sync_disk(self.ssh_handlers)
        self.rac_builder.install_grid_phase1(self.ssh_handlers[0])
        self.rac_builder.install_grid_phase2(self.ssh_handlers)
        self.rac_builder.install_grid_phase3(self.ssh_handlers[0])
        self.rac_builder.verify_grid_status(self.ssh_handlers[0])
        self.rac_builder.create_database_groups(self.ssh_handlers[0])

        self.rac_builder.unzip_database(self.ssh_handlers[0])
        self.rac_builder.install_database_phase1(self.ssh_handlers[0])
        self.rac_builder.install_database_phase2(self.ssh_handlers)
        self.rac_builder.install_database_phase3(self.ssh_handlers[0])
