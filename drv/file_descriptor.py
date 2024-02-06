from .constants import *


class FileDescriptor:
    """Represents a file in FAT8 file system."""

    def __init__(self, name, first_cluster, fat, directory):
        self.file_name = name
        self.file_size = CLUSTER_SIZE
        self.first_cluster = first_cluster
        self.current_cluster = first_cluster
        self.fat = fat
        self.dir = directory
        self.current_position = 0
        self.written = 0

    def __bytes__(self):
        fd_as_bytes = bytearray(16)
        fd_as_bytes[0:8] = bytes(self.file_name.zfill(NAME_SIZE), "utf-8")
        fd_as_bytes[8:10] = self.file_size.to_bytes(2, byteorder="little")
        fd_as_bytes[10] = self.first_cluster
        fd_as_bytes[11] = self.current_cluster
        fd_as_bytes[12:14] = self.current_position.to_bytes(2, byteorder="little")
        fd_as_bytes[14:16] = self.written.to_bytes(2, byteorder="little")
        return fd_as_bytes

    def file_truncate(self, size):
        """Edits file size."""
        if size > self.file_size:
            new_cluster = self.fat.find_free_cluster()
            self.fat.fat_table.set_on_index(self.current_cluster, new_cluster)
            self.fat.fat_table.set_on_index(new_cluster, 0)

            self.file_size = size
            self.current_cluster = new_cluster
            self.current_position = 0
        else:
            self.file_size = size
            num_of_delete = self.file_size // CLUSTER_SIZE
            clusters_to_delete = self.find_all_clusters()[-num_of_delete:]
            last_cluster = [cluster for cluster in self.find_all_clusters() if cluster not in clusters_to_delete][0]
            self.delete_clusters(clusters_to_delete)

            self.fat.fat_table.set_on_index(last_cluster, 0)
            self.current_cluster = self.find_all_clusters()[-1]
            self.current_position = 0
            self.written = self.file_size

    def file_seek(self, position):
        """Moves file pointer to given position."""
        if position < self.file_size:
            if self.current_position + position < 0:
                previous_cluster = self.first_cluster
                wanted_cluster = self.current_cluster
                while True:
                    next_cluster = self.fat.fat_table.get_on_index(previous_cluster)
                    if next_cluster == wanted_cluster:
                        break
                    previous_cluster = next_cluster
                self.current_cluster = next_cluster
                self.current_position = CLUSTER_SIZE + position + self.current_position
                return
            else:
                self.current_position += position
                return

        raise IndexError("Index out of range")

    def file_stat(self):
        """Returns size of file in bytes."""
        return self.file_size

    def file_tell(self):
        """Returns position of pointer."""
        return self.current_position

    def file_read(self, size):
        """Reads size bytes from file and moves the pointer."""
        raw_data = self.fat.read_cluster(self.current_cluster)
        self.current_position += size
        return raw_data[self.current_position: self.current_position + size]

    def file_write(self, data):
        data_length = len(data)
        self.written += data_length
        if self.written > self.file_size:
            difference_previous = self.file_size - (self.written - data_length)

            self.fat.write_cluster(self.current_cluster, data[:difference_previous], self.current_position)
            self.file_truncate(self.file_size + BLOCK_SIZE)
            self.file_write(data[difference_previous:])
        else:
            self.fat.write_cluster(self.current_cluster, data, self.current_position)
            self.current_position += data_length

    def file_close(self):
        self.dir.fat.write_cluster(self.dir.dir_cluster, self.__bytes__(), self.dir.entries.index(self) * DIR_ENTRY_SIZE)

    def file_delete(self):
        """Deletes file and free all clusters."""
        all_clusters = [self.first_cluster]
        current_cluster = all_clusters[0]
        while True:
            if self.fat.fat_table.get_on_index(current_cluster) == 0:
                self.fat.fat_table.set_on_index(current_cluster, 0xFF)
                break
            all_clusters.append(self.fat.fat_table.get_on_index(current_cluster))
            previous_cluster = current_cluster
            current_cluster = self.fat.fat_table.get_on_index(current_cluster)
            self.fat.fat_table.set_on_index(previous_cluster, 0xFF)
        for cluster in all_clusters:
            self.fat.delete_cluster(cluster)

        self.dir.remove_entry(self.file_name)

    def find_all_clusters(self):
        all_clusters = [self.first_cluster]
        current_cluster = all_clusters[0]
        while True:
            if self.fat.fat_table.get_on_index(current_cluster) == 0:
                break
            all_clusters.append(self.fat.fat_table.get_on_index(current_cluster))
            current_cluster = self.fat.fat_table.get_on_index(current_cluster)

        return all_clusters

    def delete_clusters(self, clusters):
        for cluster in clusters:
            self.fat.delete_cluster(cluster)
            self.fat.fat_table.set_on_index(cluster, 0xFF)
