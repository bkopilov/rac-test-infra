class PackageInstallation:
    pass


class PackageInstallHammer5(PackageInstallation):
    @classmethod
    def package_pre_install(cls):
        # install hammer-db inside the running container
        return """
   VERSION=`grep "VERSION_ID" /etc/os-release | cut -d'=' -f2 | tr -d '"'`
   if [ $VERSION == "9.6" ]; then
    dnf install -y https://github.com/TPC-Council/HammerDB/releases/download/v5.0/hammerdb-5.0-1.el9.x86_64.rpm
   elif [ $VERSION == "8.6" ]; then
    dnf install -y https://github.com/TPC-Council/HammerDB/releases/download/v5.0/hammerdb-5.0-1.el8.x86_64.rpm
   else
    echo "hammerdb version not supported"
   fi
   dnf install -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-basic-21.18.0.0.0-1.el8.x86_64.rpm
   dnf install -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-sqlplus-21.18.0.0.0-1.el8.x86_64.rpm

    bash -c "chmod 777 -R /opt/HammerDB-5.0/"
    """

    @classmethod
    def remove_old_packages(cls):
        return """
        bash -c "rm -rf /opt/HammerDB-5.0" 
        """