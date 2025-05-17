
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
    def copy_qdisk(cls):
        return """
        sudo dnf install -y /u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm
        echo "12345678" | su - oracle bash -c "scp /u01/app/21.0.0/grid/cv/rpm/cvuqdisk-1.0.10-1.rpm oracle@oralab2:/tmp"    
        """

    @classmethod
    def install_qdisk(cls, cvuqdisk_path):
        return f"""
        sudo dnf install -y {cvuqdisk_path}
        """
