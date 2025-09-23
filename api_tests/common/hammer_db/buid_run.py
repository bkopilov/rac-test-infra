class BuildRun:
    pass

class BuildRunHammerDB(BuildRun):
    @classmethod
    def env_params(cls):
        return """
        bash -c "cat > /opt/HammerDB-5.0/env_params << EOF
export TNS_ADMIN=/opt/HammerDB-5.0/
export ORACLE_SYSTEM_USER=system
export ORACLE_SYSTEM_PASSWORD=Password1
export ORACLE_INSTANCE=oralab
ORACLE_HOME=/usr/lib/oracle/21/client64

#small profile
export ORA_NUM_VU=1
export ORA_COUNT_WARE=1
export ORA_RAMPUP=2
export ORA_DURATION=2
export ORA_ALLWAREHOUSE=false
export HDB_PROFILE_ID=100
EOF
"
        """

    @classmethod
    def build_hammerbd(cls):
        return """
        bash -c "source /opt/HammerDB-5.0/env && /opt/HammerDB-5.0/hammerdbcli auto build.tcl"
        :return:
        """

    @classmethod
    def run_hammerbd(cls):
        return """
        bash -c "source /opt/HammerDB-5.0/env && /opt/HammerDB-5.0/hammerdbcli auto run.tcl"
        :return:
        """

    @classmethod
    def drop_hammerbd(cls):
        return """
        bash -c "source /opt/HammerDB-5.0/env && /opt/HammerDB-5.0/drop_tpcc_user.sh"
        """

