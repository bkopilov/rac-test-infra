

class PackageInstallation:
    pass


class PackageInstallation21cRac(PackageInstallation):
    @classmethod
    def package_pre_install(cls):
        return """
sudo curl -k -L https://download.eng.rdu2.redhat.com/released/rhel-8/RHEL-8/8.10.0/BaseOS/x86_64/os/Packages/\
glibc-2.28-251.el8.x86_64.rpm -o /tmp/glibc-2.28-251.el8.x86_64.rpm
sudo -i dnf install -y  /tmp/glibc-2.28-251.el8.x86_64.rpm

sudo -i dnf install -y bc binutils compat-openssl10 elfutils-libelf glibc glibc-devel ksh libaio libXrender libX11 \
libXau libXi libXtst libgcc libnsl libstdc++ libxcb libibverbs make policycoreutils \
policycoreutils-python-utils smartmontools sysstat net-tools nfs-utils

sudo curl -k -L  https://yum.oracle.com/repo/OracleLinux/OL8/appstream/x86_64/getPackage\
/oracle-database-preinstall-21c-1.0-1.el8.x86_64.rpm -o /tmp/oracle-database-preinstall-21c-1.0-1.el8.x86_64.rpm

sudo -i dnf install -y /tmp/oracle-database-preinstall-21c-1.0-1.el8.x86_64.rpm

"""
    @classmethod
    def create_tmp_exec(cls):
        return """
        sudo mount -t tmpfs -o exec,rw tmpfs /tmp
        """
