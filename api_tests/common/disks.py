import copy
import json
import logging
from collections import OrderedDict


logger = logging.getLogger(__name__)


class CleanNodeDisks:

    """ Clean node disks when baremetal deployment
    When installing a cluster with extra disks for operators , other disks content changed
    On next installation cycle the same disk may fail the installation because its not empty
    On operators / installation disk chosen per best match but content was not removed,
    only installation disk formatted
    """

    list_disks_cmd = "sudo -i lsblk -J"
    lvremove = "sudo -i lvremove --force "
    vgremove = "sudo -i vgremove --force "

    def __init__(self, node):
        self.node = node

    def _clean_lvm(self, name):
        # clean lvm types lvs vgs when possible
        vg_name = name.split("-")[0]
        lv_name = name.split("-")[1]
        lv_dev = f"/dev/{vg_name}/{lv_name}"
        try:
            self.node.run_command(f"{self.lvremove} {lv_dev}")
            self.node.run_command(f"{self.vgremove} {vg_name}")
        except RuntimeError as e:




            logger.info(f"Unable to delete lvm - probably already deleted, error: {str(e)}")

    def _clean_disk(self, name):
        # clean  disk types
        cmd = f"sudo -i wipefs --force -a  /dev/{name}"
        self.node.run_command(cmd)

    def _clean_raid(self, name):
        # clean md and raid disk types when possible
        cmd = f"sudo -i mdadm -S /dev/{name}"
        try:
            self.node.run_command(cmd)
        except RuntimeError as e:
            logger.info(f"Command {cmd} failed - probably already deleted, error: {str(e)}")

    def _disks(self, filter_type=None):
        """Disk entry to filter by : disk, lvm or raid
        {
         "name": "nvme3n1",
         "maj:min": "259:3",
         "rm": false,
         "size": "1.5T",
         "ro": false,
         "type": "disk",
         "mountpoints": [
             null
         ],
         "children": [
            {
               "name": "md127",
               "maj:min": "9:127",
               "rm": false,
               "size": "2.9T",
               "ro": false,
               "type": "raid0",
               "mountpoints": [
                   null
               ]
            }
         callback example: lambda entry: "loop" in entry['type']
        """
        disks = self.node.run_command(self.list_disks_cmd)
        json_disks = json.loads(disks)['blockdevices']

        # flatten the lsblk json to a list of dicts , children contains disk types too when dependency
        for d in json_disks:
            if d.get('children'):
                json_disks.extend(copy.deepcopy(d['children']))
                d['children'] = None

        if not filter_type:
            return json_disks

        filtered_disk = []
        for disk in json_disks:
            if filter_type in disk['type']:
                filtered_disk.append(disk)

        return filtered_disk

    def clean_disks(self):
        disks_clean_action = OrderedDict()
        disks_clean_action["lvm"] = self._clean_lvm
        disks_clean_action["md"] = self._clean_raid
        disks_clean_action["raid"] = self._clean_raid
        disks_clean_action["disk"] = self._clean_disk

        for disk_type, func in disks_clean_action.items():
            disks_to_clean = self._disks(filter_type=disk_type)
            for disk in disks_to_clean:
                func(disk['name'])