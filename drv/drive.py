import uuid

from .cache import Cache
from .constants import *


class Drive:
    """Represents hard drive as file."""

    def __init__(self, file, size):
        """Creates new drive.

        Args:
            file: path to file that will represent drive
            size: number of 512 B block in drive
        """
        with open(file, "wb") as drive:
            drive.write(b'\x00' * (size * BLOCK_SIZE))

        self.drive_id = uuid.uuid4()
        self.file = file
        self.size = size
        self.opened = False
        self.cache = Cache(self.drive_id, CACHE_SIZE)
        self.clock = 0

    def drv_open(self):
        self.opened = True

    def drv_close(self):
        self.opened = False

    def drv_stat(self):
        """Returns size of opened drive in blocks."""
        if self.opened:
            return self.size
        return False

    def clock_manage(self):
        """Manages clock cycle for cache."""
        self.clock += 1

        if self.clock == CLOCK_CYCLE:
            self.clock = 0
            self.cache.free()

    def drv_write(self, block_id, data):
        self.clock_manage()
        self.cache.write(block_id, data)

        with open(self.file, "r+b") as drive:
            drive.seek((block_id - 1) * BLOCK_SIZE)  # move on the right position (block)
            drive.write(data)

    def drv_read(self, block_id):
        cached_data = self.cache.read(block_id)
        if cached_data:
            return cached_data
        else:
            with open(self.file, "rb") as drive:
                drive.seek((block_id - 1) * BLOCK_SIZE)
                read_data = drive.read(BLOCK_SIZE)

        return read_data
