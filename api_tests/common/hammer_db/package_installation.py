class PackageInstallation:
    pass


class PackageInstallHammer5(PackageInstallation):
    @classmethod
    def package_pre_install(cls):
        return """
        if rpm -q --quiet hammerdb-5.0-1.el8.x86_64; then
  echo "hammerdb-5.0-1.el8.x86_64 is installed - reinstalling."
  sudo -i dnf reinstall -y https://github.com/TPC-Council/HammerDB/releases/download/v5.0/hammerdb-5.0-1.el8.x86_64.rpm
else
  echo "hammerdb-5.0-1.el8.x86_64 is not installed."
  sudo -i dnf install -y https://github.com/TPC-Council/HammerDB/releases/download/v5.0/hammerdb-5.0-1.el8.x86_64.rpm
fi

if rpm -q --quiet oracle-instantclient-basic-21.18.0.0.0-1.el8.x86_64; then
  echo "hammerdb-5.0-1.el8.x86_64 is installed. - reinstalling"
  sudo -i dnf reinstall -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-basic-21.18.0.0.0-1.el8.x86_64.rpm
else
  echo "hammerdb-5.0-1.el8.x86_64 is not installed."
  sudo -i dnf install -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-basic-21.18.0.0.0-1.el8.x86_64.rpm
fi

if rpm -q --quiet oracle-instantclient-sqlplus-21.18.0.0.0-1.el8.x86_64; then
  echo "hammerdb-5.0-1.el8.x86_64 is installed - reinstalling."
  sudo -i dnf reinstall -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-sqlplus-21.18.0.0.0-1.el8.x86_64.rpm
else
  echo "hammerdb-5.0-1.el8.x86_64 is not installed."
  sudo -i dnf install -y https://download.oracle.com/otn_software/linux/instantclient/2118000/oracle-instantclient-sqlplus-21.18.0.0.0-1.el8.x86_64.rpm
fi
    """

    @classmethod
    def remove_old_packages(cls):
        return """
        sudo -i rm -rf /opt/HammerDB-5.0 
        """