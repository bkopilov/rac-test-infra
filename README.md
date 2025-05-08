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


