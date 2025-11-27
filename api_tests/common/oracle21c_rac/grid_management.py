

class GridManagement:
    pass


class GridManagement21cRac(GridManagement):

    @classmethod
    def validate_grid_preinstall(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/runcluvfy.sh stage -pre crsinst -n 'oralab1,oralab2'"
        """

    @classmethod
    def grid_install_phase1(cls, **params):
        """ Grid phase 1 support params - update the file - TBD.
        :param params:
        :return:
        """
        output = """
         echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/gridSetup.sh -ignorePrereq -waitforcompletion -silent \
        -responseFile /u01/app/21.0.0/grid/install/response/gridsetup.rsp \
        INVENTORY_LOCATION=/u01/app/oraInventory \
        oracle.install.option=CRS_CONFIG \
        ORACLE_BASE=/u01/app/oracle \
        oracle.install.asm.OSDBA=asmdba \
        oracle.install.asm.OSASM=asmadmin \
        oracle.install.crs.config.scanType=LOCAL_SCAN \
        oracle.install.crs.config.gpnp.scanName=oralab-scan \
        oracle.install.crs.config.gpnp.scanPort=1521 \
        oracle.install.crs.config.ClusterConfiguration=STANDALONE \
        oracle.install.crs.config.configureAsExtendedCluster=false \
        oracle.install.crs.config.clusterName=oralab2-cl \
        oracle.install.crs.config.gpnp.configureGNS=false \
        oracle.install.crs.config.autoConfigureClusterNodeVIP=false \
        oracle.install.crs.config.clusterNodes=oralab1.oracle-rac.openinfra.lab:oralab1-vip.oracle-rac.openinfra.lab,oralab2.oracle-rac.openinfra.lab:oralab2-vip.oracle-rac.openinfra.lab \
        oracle.install.crs.config.networkInterfaceList=eth0:192.168.120.0:1,eth1:192.168.121.0:5 \
        oracle.install.crs.configureGIMR=false \
        oracle.install.crs.config.storageOption=FLEX_ASM_STORAGE \
        oracle.install.crs.config.useIPMI=false \
        oracle.install.asm.diskGroup.name=OCR \
        oracle.install.asm.diskGroup.redundancy=EXTERNAL \
        oracle.install.asm.diskGroup.AUSize=4 \
        oracle.install.asm.diskGroup.disksWithFailureGroupNames=/dev/oracleasm/asmdisk1, \
        oracle.install.asm.diskGroup.disks=/dev/oracleasm/asmdisk1 \
        oracle.install.asm.diskGroup.diskDiscoveryString=/dev/oracleasm/* \
        oracle.install.asm.monitorPassword=Password1 \
        oracle.install.asm.SYSASMPassword=Password1 \
        oracle.install.asm.configureAFD=false \
        oracle.install.crs.configureRHPS=false \
        oracle.install.crs.config.ignoreDownNodes=false \
        oracle.install.config.managementOption=NONE \
        oracle.install.config.omsPort=0 \
        oracle.install.crs.rootconfig.executeRootScript=false"
        """
        return output

    @classmethod
    def grid_install_phase2_1(cls):
        return """
        sudo -i /u01/app/oraInventory/orainstRoot.sh
        """

    @classmethod
    def grid_install_phase2_2(cls):
        return """
            sudo -i /u01/app/21.0.0/grid/root.sh
            """

    @classmethod
    def grid_install_phase3(cls, **params):
        """ Grid phase 3 support params - update the file - TBD.
               :param params:
               :return:
        """
        output = """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/gridSetup.sh -silent -executeConfigTools \
        -responseFile /u01/app/21.0.0/grid/install/response/gridsetup.rsp \
        INVENTORY_LOCATION=/u01/app/oraInventory \
        oracle.install.option=CRS_CONFIG \
        ORACLE_BASE=/u01/app/oracle \
        oracle.install.asm.OSDBA=asmdba \
        oracle.install.asm.OSASM=asmadmin \
        oracle.install.crs.config.scanType=LOCAL_SCAN \
        oracle.install.crs.config.gpnp.scanName=oralab-scan \
        oracle.install.crs.config.gpnp.scanPort=1521 \
        oracle.install.crs.config.ClusterConfiguration=STANDALONE \
        oracle.install.crs.config.configureAsExtendedCluster=false \
        oracle.install.crs.config.clusterName=oralab2-cl \
        oracle.install.crs.config.gpnp.configureGNS=false \
        oracle.install.crs.config.autoConfigureClusterNodeVIP=false \
        oracle.install.crs.config.clusterNodes=oralab1.oracle-rac.openinfra.lab:oralab1-vip.oracle-rac.openinfra.lab,oralab2.oracle-rac.openinfra.lab:oralab2-vip.oracle-rac.openinfra.lab \
        oracle.install.crs.config.networkInterfaceList=eth0:192.168.120.0:1,eth1:192.168.121.0:5 \
        oracle.install.crs.configureGIMR=false \
        oracle.install.crs.config.storageOption=FLEX_ASM_STORAGE \
        oracle.install.crs.config.useIPMI=false \
        oracle.install.asm.diskGroup.name=OCR01 \
        oracle.install.asm.diskGroup.redundancy=EXTERNAL \
        oracle.install.asm.diskGroup.AUSize=4 \
        oracle.install.asm.diskGroup.disksWithFailureGroupNames=/dev/oracleasm/asmdisk1, \
        oracle.install.asm.diskGroup.disks=/dev/oracleasm/asmdisk1 \
        oracle.install.asm.diskGroup.diskDiscoveryString=/dev/oracleasm/* \
        oracle.install.asm.monitorPassword=Password1 \
        oracle.install.asm.SYSASMPassword=Password1 \
        oracle.install.asm.configureAFD=false \
        oracle.install.crs.configureRHPS=false \
        oracle.install.crs.config.ignoreDownNodes=false \
        oracle.install.config.managementOption=NONE \
        oracle.install.config.omsPort=0 \
        oracle.install.crs.rootconfig.executeRootScript=false"
        """
        return output

    @classmethod
    def grid_crsctl_stat(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/bin/crsctl stat res -t"
    """

    @classmethod
    def grid_disk_group_stat(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/bin/asmcmd -p lsdg"
        """