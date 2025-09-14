
class HostFile:
    pass

class HostFileSetting(HostFile):

    @classmethod
    def set_hosts_file(cls):
        return """
        sudo bash -c "cat > /tmp/hosts <<EOF
192.168.120.69  oralab-scan.oracle-rac.openinfra.lab  oralab-scan
192.168.120.70  oralab-scan.oracle-rac.openinfra.lab  oralab-scan
192.168.120.71  oralab-scan.oracle-rac.openinfra.lab  oralab-scan
192.168.120.201  oralab1-vip.oracle-rac.openinfra.lab  oralab1-vip
192.168.120.202  oralab2-vip.oracle-rac.openinfra.lab  oralab2-vip
192.168.120.101  oralab1.oracle-rac.openinfra.lab  oralab1
192.168.120.102  oralab2.oracle-rac.openinfra.lab  oralab2
EOF"

sudo cp /tmp/hosts /etc/hosts

        """