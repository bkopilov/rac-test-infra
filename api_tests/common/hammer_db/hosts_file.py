
class HostFile:
    pass

class HostFileSetting(HostFile):

    @classmethod
    def set_resolv_file(cls):
        return """
        bash -c "cat > /tmp/resolv.conf <<EOF
        nameserver 192.168.120.1
EOF"
bash -c "cp /tmp/resolv.conf  /etc/resolv.conf"

        """

    @classmethod
    def save_resolv_file(cls):
        return """
        bash -c "/usr/bin/cp /etc/resolv.conf /tmp/resolv.conf.bk"
        """

    @classmethod
    def restore_resolv_file(cls):
        return """
        bash -c "cp /tmp/resolv.conf.bk /etc/resolv.conf"
        """