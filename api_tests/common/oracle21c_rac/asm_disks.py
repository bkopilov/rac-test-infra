class AsmDisks:
    pass


class AsmDisks21cRac(AsmDisks):

    @classmethod
    def create_disk_partition(cls, disk):
        return f"""
        sudo echo -e 'n\\np\\n1\\n\\n\\nw' | sudo fdisk /dev/{disk}
        sudo partprobe
        """

    @classmethod
    def disk_id(cls, disk):
        # name by disk vda , sda without /dev
        return f"""
        sudo find /dev/disk/by-id/ -lname *{disk} -printf "%f\n" | head -n 1
        """

    @classmethod
    def create_udev(cls, disk_id1, disk_id2, disk_id3):
        return f"""
        cat > /tmp/99-oracle-asmdevices.rules <<EOF
KERNEL=="sd?1", SUBSYSTEM=="block", PROGRAM=="/usr/lib/udev/scsi_id -g -u -d /dev/\$parent", RESULT=="{disk_id1}", SYMLINK+="oracleasm/asmdisk1", OWNER="oracle", GROUP="asmadmin", MODE="0660"
KERNEL=="sd?1", SUBSYSTEM=="block", PROGRAM=="/usr/lib/udev/scsi_id -g -u -d /dev/\$parent", RESULT=="{disk_id2}", SYMLINK+="oracleasm/asmdisk2", OWNER="oracle", GROUP="asmadmin", MODE="0660"
KERNEL=="sd?1", SUBSYSTEM=="block", PROGRAM=="/usr/lib/udev/scsi_id -g -u -d /dev/\$parent", RESULT=="{disk_id3}", SYMLINK+="oracleasm/asmdisk3", OWNER="oracle", GROUP="asmadmin", MODE="0660"
EOF
        sudo -i bash -c "cp /tmp/99-oracle-asmdevices.rules /etc/udev/rules.d/99-oracle-asmdevices.rules"
"""

    @classmethod
    def reload_udev_rules(cls):
        return """
        sudo -i /sbin/udevadm control --reload-rules
        sudo -i /sbin/udevadm trigger --action=add
        sudo sleep 3
        sudo -i ls -l /dev/oracleasm/
        """

    @classmethod
    def sync_disks(cls):
        return """
        sudo -i partprobe
        """
