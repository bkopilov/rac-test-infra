```
# rac-test-infra
Create cluster with with ocpv vms and create RAC cluster.
RAC cluster on OCPv will be connected to shared volumes ODF or iSCSI netapp
Added additional nics for RAC network - private and public

Test run on baremetal node , create a cluster on libvirt with virtual machines
Install cluster with assisted-test-infra framework(upstream) , enabled needed operators

Runing test:
git config --global http.sslVerify false
cd /home/benny/
git clone https://github.com/openshift/assisted-test-infra
git clone https://github.com/bkopilov/rac-test-infra.git
cd assisted-test-infra
make image_build 

Test params before running:
export OPENSHIFT_VERSION="4.18"
export REMOTE_SERVICE_URL="https://api.stage.openshift.com"
export AUTH_TYPE=rhsso
export SSO_URL="https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
export PYTHONPATH="/home/benny/assisted-test-infra/src"
export TEST="/home/benny/rac-test-infra/api_tests/"
export TEST_FUNC=test_create_rac_deployment
export TEST_TEARDOWN="false"
export SSH_PUB_KEY="$(cat /root/.ssh/id_rsa.pub)"
token and pull secrect from https://console.redhat.com/openshift/downloads
export OFFLINE_TOKEN=
export PULL_SECRET=

Run test:
make test 

In order to access to the clusters console from laptop need to :

Update /etc/hosts to the hypervisor
Example:
10.9.76.8 	api.test-infra-cluster-97a2d146.redhat.com
10.9.76.8	oauth-openshift.apps.test-infra-cluster-97a2d146.redhat.com
10.9.76.8	console-openshift-console.apps.test-infra-cluster-97a2d146.redhat.com

From the Hypervisor need to add nat redirect to the API address on 443:
Adding source of laptop will prevent issue with access to port 443 for other services

tunnel=x.y.z.v # source
sudo iptables -t nat -A PREROUTING -s $tunnel   -p tcp --dport 80 -j DNAT --to-destination 192.168.127.100:80
sudo iptables -t nat -A PREROUTING  -s  $tunnel   -p tcp --dport 443 -j DNAT --to-destination 192.168.127.100:443

```
