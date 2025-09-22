
class BinariesManagement:
    pass


class Binaries21cRac(BinariesManagement):

    @classmethod
    def download_binaries(cls, url):
        return f"""
        sudo curl -k -L {url} -o /tmp/{url.split("/")[-1]}
        """

    @classmethod
    def unzip_grid_binary(cls, url):
        return f"""
          echo "12345678" | su - oracle bash -c "unzip /tmp/{url.split("/")[-1]} -d /u01/app/21.0.0/grid"
        """

    @classmethod
    def unzip_database_binary(cls, url):
        return f"""
        echo "12345678" | su - oracle bash -c "unzip /tmp/{url.split("/")[-1]} -d /u01/app/oracle/product/21.0.0.0/dbhome_1"
        """

    @classmethod
    def create_database_dir(cls):
        return """
        echo "12345678" | su - oracle bash -c "mkdir -p /u01/app/oracle/product/21.0.0.0/dbhome_1"
        """
    @classmethod
    def copy_qdisk(cls):
        return """
        sudo -i dnf install -y /u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm
        echo "12345678" | su - oracle bash -c "scp /u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm oracle@oralab2:/tmp"    
        """

    @classmethod
    def install_qdisk(cls, cvuqdisk_path):
        return f"""
        sudo -i dnf install -y {cvuqdisk_path}
        """

    @classmethod
    def huge_pages(cls, size="512"):
        return f"""
        sudo -i sysctl -w vm.nr_hugepages={size}
        """
