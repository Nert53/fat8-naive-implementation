from .constants import *


class FatTable:
    """Represent FAT table in my FAT8"""

    def __init__(self, fat):
        self.table = []
        self.fat = fat

        for _ in range(self.fat.drive.drv_stat() - FIRST_DATA_BLOCK):
            self.table.append(0xFF)

    def __bytes__(self):
        return bytearray(self.table)

    def fat_table_stat(self):
        """Return how many records does FAT have."""
        return len(self.table)

    def set_on_index(self, index, value):
        if index < (self.fat.drive.drv_stat() - FIRST_DATA_BLOCK):
            self.table[index] = value
            tbl = self.__bytes__()
            self.fat.drive.drv_write(FAT_TABLE_BLOCK, tbl)
        else:
            raise IndexError("Index out of range")

    def get_on_index(self, index):
        if index < (self.fat.drive.drv_stat() - FIRST_DATA_BLOCK):
            return self.table[index]
        else:
            raise IndexError("Index out of range")
