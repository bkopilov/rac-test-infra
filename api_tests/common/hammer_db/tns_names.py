import unittest


class TnsNames(object):
    pass

class TnsNamesOracle(TnsNames):
    @classmethod
    def tns_name_configuration(cls):
        return """
        bash -c "cat > /opt/HammerDB-5.0/tnsnames.ora << EOF
ORALAB =
  (DESCRIPTION =
	(ADDRESS_LIST =
  	(ADDRESS = (PROTOCOL = TCP)(HOST = oralab-scan.oracle-rac.openinfra.lab )(PORT = 1521))
	)
	(CONNECT_DATA =
  	(SID = pdb1)
 	(SERVICE_NAME = pdb1)
	)
  )
EOF
"
        """