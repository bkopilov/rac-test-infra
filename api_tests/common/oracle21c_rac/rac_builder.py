from .repo_creation import RepoCreation21cRac
from .users_management import UsersManagement21cRac
from .package_installation import PackageInstallation21cRac
from .binaries_management import Binaries21cRac
from .grid_management import GridManagement21cRac


class RacBuilder:
    pass


class Builder21cRac(RacBuilder):
    def __init__(self, download_binaries):
        self.repo_creation = RepoCreation21cRac
        self.package_installation = PackageInstallation21cRac
        self.user_management = UsersManagement21cRac
        self.binaries_management = Binaries21cRac
        self.grid_management = GridManagement21cRac
        self.download_binaries = download_binaries

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
        for ssh_handler in ssh_handlers:
            ssh_handler.execute(groups_cmd)
            ssh_handler.execute(ssh_keys_cmd)
            ssh_handler.execute(directories_cmd)

    def create_authorized_keys(self, ssh_handlers):
        get_public_cmd = self.user_management.get_public_key()
        rsa_public1_cmd = ssh_handlers[0].execute(get_public_cmd)
        rsa_public2_cmd = ssh_handlers[1].execute(get_public_cmd)
        update_public1 = self.user_management.update_authorized_key(rsa_public1_cmd)
        update_public2 = self.user_management.update_authorized_key(rsa_public2_cmd)

        ssh_handlers[0].execute(update_public2)
        ssh_handlers[1].execute(update_public1)

    def create_ssh_known_hosts(self, ssh_handlers):
        key_scan1_cmd = self.user_management.ssh_key_scans(ssh_handlers[0].ssh_ipv4)
        key_scan2_cmd = self.user_management.ssh_key_scans(ssh_handlers[1].ssh_ipv4)
        ssh_handlers[0].execute(key_scan2_cmd)
        ssh_handlers[1].execute(key_scan1_cmd)

    def download_binaries(self, ssh_handler):
        for bin_download in self.download_binaries:
            cmd = self.binaries_management.download_binaries(bin_download)
            ssh_handler.execute(cmd)

    def unzip_grid(self, ssh_handler):
        cmd = self.binaries_management.unzip_grid_binary(self.download_binaries[0])
        ssh_handler.execute(cmd)

    def install_qdisk(self, ssh_handlers):
        cmd = self.binaries_management.copy_qdisk()
        ssh_handlers[0].execute(cmd)
        install1 = self.binaries_management.install_qdisk("/u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm")
        ssh_handlers[0].execute(install1)
        install2 = self.binaries_management.install_qdisk("/tmp/cvuqdisk-1.0.10-1.rpm")
        ssh_handlers[1].execute(install2)

    def install_grid_perinstall(self, ssh_handler):
        cmd = self.grid_management.validate_grid_preinstall()
        ssh_handler.execute(cmd)


class RacDirector:
    def __init__(self, rac_builder, ssh_handlers):
        self.ssh_handlers = ssh_handlers
        self.rac_builder = rac_builder

    def build(self):
        self.rac_builder.create_repo(self.ssh_handlers)
        self.rac_builder.create_packages(self.ssh_handlers)
        self.rac_builder.create_users(self.ssh_handlers)
        self.rac_builder.create_authorized_keys(self.ssh_handlers)
        self.rac_builder.create_ssh_known_hosts(self.ssh_handlers)
        self.rac_builder.download_binaries(self.ssh_handlers[0])
        self.rac_builder.install_qdisk(self.ssh_handlers)
        self.rac_builder.install_grid_perinstall(self.ssh_handlers[0])
