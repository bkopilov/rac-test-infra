
class GridManagement:
    pass


class GridManagement21cRac(GridManagement):

    @classmethod
    def validate_grid_preinstall(cls):
        return """
        echo "12345678" | su - oracle bash -c "/u01/app/21.0.0/grid/runcluvfy.sh stage -pre crsinst -n 'oralab1,oralab2'"
        """

