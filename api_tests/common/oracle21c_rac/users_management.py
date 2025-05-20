class UsersManagement:
    pass


class UsersManagement21cRac(UsersManagement):

    @classmethod
    def create_users_group(cls):
        return """
    #sudo useradd oracle
    sudo echo "oracle ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/oracle
    sudo echo "12345678" | sudo passwd --stdin oracle
    # sudo groupadd -g 54321 oinstall
    sudo groupadd -g 54331 asmdba
    sudo groupadd -g 54332 asmadmin
    sudo useradd -g oinstall -G asmdba,asmadmin oracle
    sudo usermod -a -G asmadmin oracle
    sudo usermod -a -G asmdba oracle
    """

    @classmethod
    def create_ssh_keys(cls):
        return """
        echo "12345678" | su - oracle bash -c "cat /dev/zero | ssh-keygen -t rsa -q -N ''; echo"
        echo "12345678" | su - oracle bash -c "touch ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys; echo"
        echo "12345678" | su - oracle bash -c "touch ~/.ssh/authorized_keys; chmod 644 ~/.ssh/known_hosts; echo"
        
        """

    @classmethod
    def get_public_key(cls):
        return """
        echo "12345678" | su - oracle bash -c "cat /home/oracle/.ssh/id_rsa.pub"
        """.replace("\n", "")

    @classmethod
    def create_directories(cls):
        return """
        sudo mkdir -p /u01/app/21.0.0/grid
        sudo mkdir -p /u01/app/oraInventory
        sudo mkdir -p /u01/app/oracle
        sudo chown -R oracle:oinstall /u01
        sudo chmod -R 775 /u01
        """

    @classmethod
    def enable_services(cls):
        return """
        sudo -i systemctl enable chronyd.service
        sudo -i chronyc -a 'burst 4/4'
        sudo -i chronyc -a makestep 
        sudo -i bash -c "echo 'server clock.redhat.com' >> /etc/chrony.conf"
        sudo -i systemctl restart chronyd
        """

    @classmethod
    def create_swap(cls):
        return """
        sudo -i bash -c "dd if=/dev/zero of=/swap.img bs=1 count=0 seek=17G"
        sudo -i bash -c "losetup /dev/loop0 /swap.img"
        sudo -i bash -c "mkswap /dev/loop0"
        sudo -i bash -c "swapon -v /dev/loop0"
        sudo -i bash -c "echo '/dev/loop0   none                    swap    defaults        0 0' >> /etc/fstab"
        """

    @classmethod
    def update_authorized_key(cls, id_rsa_pub):
        return f""" 
        echo "12345678" | su - oracle bash -c "echo '{id_rsa_pub}' >> /home/oracle/.ssh/authorized_keys"
        """

    @classmethod
    def ssh_key_scans(cls, ipv4_address):
        return f"""
        echo "12345678" | su - oracle bash -c "ssh-keyscan -H {ipv4_address} >> /home/oracle/.ssh/known_hosts"
        """

    @classmethod
    def ssh_strict_host_checking(cls):
        return f"""
                echo "12345678" | su - oracle bash -c "echo -e 'Host *\n StrictHostKeyChecking no'>/home/oracle/.ssh/config"
        """
