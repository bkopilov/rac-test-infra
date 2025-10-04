

class RepoCreation:
    pass


class RepoCreation21cRac(RepoCreation):

    @classmethod
    def create_repo(cls, base_url="https://download.eng.rdu2.redhat.com/released/rhel-8/RHEL-8/", version="8.10.0"):
        return f'''sudo bash -c "cat > /tmp/rhel-{version}.repo << EOF
[rhosp-{version}-baseos]
name={version} baseos
baseurl={base_url}{version}/BaseOS/x86_64/os/
enabled=1
gpgcheck=0

[rhosp-{version}-appstream]
name={version} appstream
baseurl={base_url}{version}/AppStream/x86_64/os/
enabled=1
gpgcheck=0
EOF"
sudo cp /tmp/rhel-{version}.repo /etc/yum.repos.d/rhel-{version}.repo
'''

    @classmethod
    def create_ssl_verify(cls, ssl_verify="false"):
        return f'''sudo bash -c "cat > /tmp/yum.conf << EOF
[main]
gpgcheck=0
installonly_limit=3
clean_requirements_on_remove=True
best=True
sslverify={ssl_verify}
EOF"
sudo cp  /tmp/yum.conf  /etc/yum.conf
sudo -i setenforce 0
'''
