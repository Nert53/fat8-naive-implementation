from .file_descriptor import FileDescriptor
from .constants import *


class DirEntry:
    """Represents a directory in FAT8 file system."""

    def __init__(self, name, cluster, is_directory, fat):
        self.name = name
        self.dir_cluster = cluster
        self.is_directory = is_directory
        self.fat = fat
        self.entries = []

    def __bytes__(self):
        return bytearray(self.entries)

    def entry_count(self):
        """Returns number of entries in directory."""
        return len(self.entries)

    def find_file(self, file_name):
        """Returns file descriptor if file exists in directory."""
        match = [entry for entry in self.entries if entry.file_name == file_name]
        if match:
            return match[0]

        return False

    def file_open(self, file_name):
        if len(file_name) > NAME_SIZE:
            raise ValueError("File name is too long")
        if self.find_file(file_name):
            return self.find_file(file_name)
        else:
            new_file = FileDescriptor(file_name, self.fat.find_free_cluster(), self.fat, self)
            self.fat.fat_table.set_on_index(new_file.first_cluster, 0)

        self.add_entry(new_file)
        return new_file

    def add_entry(self, file):
        """Adds entry to directory entries."""
        self.fat.write_cluster(self.dir_cluster, file.__bytes__(), self.entry_count() * DIR_ENTRY_SIZE)
        self.entries.append(file)

    def remove_entry(self, file_name):
        """Removes entry from directory entries."""
        file = self.find_file(file_name)
        if file:
            dir_entry_number = self.entries.index(file)
            self.entries.remove(file)
            self.fat.write_cluster(self.dir_cluster, '\x00' * DIR_ENTRY_SIZE, dir_entry_number * DIR_ENTRY_SIZE)
