class DataBaseManagement:
    pass


class DataBaseManagement21cRac(DataBaseManagement):

    @classmethod
    def create_data_disk_group(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/bin/asmca -silent -createDiskGroup \
       -diskGroupName DATA01 \
           -disk '/dev/oracleasm/asmdisk2' \
       -redundancy EXTERNAL \
       -au_size 4"
        """

    @classmethod
    def create_recovery_disk_group(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/bin/asmca -silent -createDiskGroup \
       -diskGroupName REC01 \
           -disk '/dev/oracleasm/asmdisk3' \
       -redundancy EXTERNAL \
       -au_size 4"
        """

    @classmethod
    def copy_listener_ora(cls):
        return """
        echo "12345678" | su - oracle bash -c "cp -p /u01/app/21.0.0/grid/network/admin/listener.ora /u01/app/oracle/product/21.0.0.0/dbhome_1/network/admin/"

        """

    @classmethod
    def install_database_phase1(cls, **params):
        output = """
        echo "12345678" | su - oracle bash -c "/u01/app/oracle/product/21.0.0.0/dbhome_1/runInstaller -debug -ignorePrereq -waitforcompletion -silent \
        -responseFile /u01/app/oracle/product/21.0.0.0/dbhome_1/install/response/db_install.rsp \
        oracle.install.option=INSTALL_DB_SWONLY \
        UNIX_GROUP_NAME=oinstall \
        INVENTORY_LOCATION=/u01/app/oraInventory \
        ORACLE_HOME=/u01/app/oracle/product/21.0.0.0/dbhome_1 \
        ORACLE_BASE=/u01/app/oracle \
        oracle.install.db.InstallEdition=EE \
        oracle.install.db.OSDBA_GROUP=oinstall \
        oracle.install.db.OSBACKUPDBA_GROUP=oinstall \
        oracle.install.db.OSDGDBA_GROUP=oinstall \
        oracle.install.db.OSKMDBA_GROUP=oinstall \
        oracle.install.db.OSRACDBA_GROUP=oinstall \
        oracle.install.db.CLUSTER_NODES=oralab1,oralab2 \
        oracle.install.db.isRACOneInstall=false \
        oracle.install.db.rac.serverpoolCardinality=0 \
        oracle.install.db.config.starterdb.type=GENERAL_PURPOSE \
        oracle.install.db.ConfigureAsContainerDB=false \
        SECURITY_UPDATES_VIA_MYORACLESUPPORT=false \
        DECLINE_SECURITY_UPDATES=true"
        """
        return output

    @classmethod
    def install_database_phase2(cls):
        return """
        sudo -i /u01/app/oracle/product/21.0.0.0/dbhome_1/root.sh
        """

    @classmethod
    def install_database_phase3(cls, **params):
        output = """
        echo "12345678" | su - oracle bash -c "/u01/app/oracle/product/21.0.0.0/dbhome_1/bin/dbca -silent -createDatabase \
        -templateName General_Purpose.dbc \
        -gdbname TESTDB01 -responseFile NO_VALUE \
        -characterSet AL32UTF8 \
        -sysPassword Password1 \
        -systemPassword Password1 \
        -createAsContainerDatabase true \
        -numberOfPDBs 1 \
        -pdbName pdb1 \
        -pdbAdminPassword Password1 \
        -databaseType MULTIPURPOSE \
        -automaticMemoryManagement false \
        -totalMemory 2048 \
        -redoLogFileSize 50 \
        -emConfiguration NONE \
        -ignorePreReqs \
        -nodelist oralab1,oralab2 \
        -storageType ASM \
        -diskGroupName +DATA01 \
        -recoveryGroupName +REC01 \
        -useOMF true \
        -asmsnmpPassword Password1"
        """
        return output