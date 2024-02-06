from drv import Drive, Fat
import hexdump


def main():
    # Prepare drive
    drive01 = Drive("drives/drive02.txt", 256)
    drive01.drv_open()
    print(f"Size of drive is: {drive01.drv_stat()}")

    # Prepare FAT
    fat01 = Fat()
    fat01.fs_format(drive01)
    fat01.fs_open()

    # Create files
    file01 = fat01.file_open("file01")
    file02 = fat01.file_open("file02")

    # Write alternately to both files
    for _ in range(5):
        file01.file_write('Lorem ipsum dolor sit amet')
        file02.file_write('Toto je zkouska hello world')

    # Write long text to file (must truncate file automatically)
    long_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.Toto je text, ktery se bude cist v dalsim kroku ukazky."""
    file01.file_write(long_text)

    # Move in file back
    print(f"Position before seek: {file01.file_tell()}")
    file01.file_seek(-30)
    print(f"Position after seek: {file01.file_tell()}")

    # Read from file
    print(f"Read text: {file01.file_read(15).decode('utf-8')}")
    file01.file_seek(-15)
    print(f"Read text: {file01.file_read(15).decode('utf-8')}")
    file01.file_seek(-55)
    print(f"Read text: {file01.file_read(15).decode('utf-8')}")

    # Print file into console with hexdump
    print("\n\t\t\t\t____Hexdump of small part of file02____")
    bytes_to_read = 256
    offset = 2048
    with open("drives/drive02.txt", "rb") as d:
        d.seek(offset)
        line = d.read(bytes_to_read)
        hexdump.hexdump(line)

    # Ending work
    file01.file_close()
    file02.file_close()
    fat01.fs_close()
    drive01.drv_close()


if __name__ == "__main__":
    main()
