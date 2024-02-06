class Cache:
    """Represents write-through cache with second chance algorithm."""

    def __init__(self, drive, size: int):
        self.cached_drive = drive
        self.size_block = int(size)
        self.storage = []

        for _ in range(self.size_block):
            self.storage.append({"used": False, "reference_bit": False, "block_id": None, "data": None})

    def free(self):
        """Frees cache."""
        for block in self.storage:
            block["reference_bit"] = False

    def write(self, block_id, data):
        """Writes one record to cache."""
        same_block = None
        unused_block = None
        unreferenced_block = None
        position = 0
        for block in self.storage:
            if block["block_id"] == block_id:       # if block is already cached I will place it on the same place
                same_block = position
            if not block["used"]:
                unused_block = position
            if not block["reference_bit"]:
                unreferenced_block = position
            position += 1

        if same_block is not None:
            self.cache_block(same_block, block_id, data)
            return True
        if unused_block is not None:
            self.cache_block(unused_block, block_id, data)
            return True
        if unreferenced_block is not None:
            self.cache_block(unreferenced_block, block_id, data)
            return True

        return False

    def cache_block(self, cache_position, block_id, data):
        """Caches block on given cache position."""
        self.storage[cache_position] = {"used": True,
                                        "reference_bit": True,
                                        "block_id": block_id,
                                        "data": data}

    def read(self, block_id):
        """Reads one block from cache or return False."""
        for block in self.storage:
            if block["used"] and block["block_id"] == block_id:
                block["reference_bit"] = True
                return block["data"]

        return False
