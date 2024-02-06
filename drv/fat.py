import json
import uuid

from .constants import *
from .drive import Drive
from .fat_table import FatTable
from .dir_entry import DirEntry


class Fat:
    """Represents a FAT8 file system."""

    def __init__(self):
        self.cluster_size = None
        self.drive = None
        self.fat_table = None
        self.root_dir = None
        self.boot_sector = None
        self.opened = False

    def boot_sector_in_bytes(self):
        return bytes(json.dumps(self.boot_sector), "utf-8")

    def fs_format(self, drive: Drive):
        """Formats drive to FAT8."""
        self.drive = drive
        self.cluster_size = CLUSTER_SIZE
        self.fat_table = FatTable(self)
        self.root_dir = DirEntry("root", ROOT_DIR_CLUSTER, True, self)
        self.boot_sector = {"root_dir_id": uuid.uuid4().__str__(),    # converting to str because of binary writing
                            "cluster_size": self.cluster_size,
                            "drive_size": self.drive.drv_stat()}

        drive.drv_write(1, self.boot_sector_in_bytes())     # first block has info about file system
        drive.drv_write(2, self.fat_table.__bytes__())      # second block contains FAT table (record is 8 B)

    def fs_open(self):
        self.opened = True
        return self

    def fs_close(self):
        self.opened = False

    def file_open(self, file_name):
        if self.opened:
            return self.root_dir.file_open(file_name)

        raise ValueError("File system is not opened")

    def file_readdir(self):
        """Returns list of file names in directory."""
        if self.opened:
            return [entry.file_name for entry in self.root_dir.entries]

        return ValueError("File system is not opened")

    def find_free_cluster(self):
        for cluster_id in range(1, self.fat_table.fat_table_stat()):
            if self.fat_table.table[cluster_id] == 0xFF:
                return cluster_id

        return False

    def write_cluster(self, cluster_id, data, offset):
        """Writes cluster of data."""
        old_data = bytearray(self.drive.drv_read(cluster_id + FIRST_DATA_BLOCK))
        if isinstance(data, str):
            data = bytes(data, "utf-8")
        pos = 0
        old_data[offset + pos: offset + pos + len(data)] = data
        self.drive.drv_write(cluster_id + FIRST_DATA_BLOCK, old_data)

    def read_cluster(self, cluster_id):
        """Reads data of size from given cluster."""
        return self.drive.drv_read(cluster_id + FIRST_DATA_BLOCK)

    def delete_cluster(self, cluster_id):
        """Deletes cluster."""
        self.drive.drv_write(cluster_id + FIRST_DATA_BLOCK, b'\x00' * CLUSTER_SIZE)
