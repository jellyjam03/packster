import sys
import os.path

comms_to_desc = {
    "create_archive": 'Create an archive\nUsage: python main.py create_archive destination name [file(s)] OR directory\n',
    "list_content": 'List content of archive\nUsage: python main.py list_content archive\n',
    "full_unpack": 'Unpacks all the content of an archive to a specified destination\nUsage: python main.py full_unpack archive destination\n',
    "unpack": 'Unpacks some files of the archive to a specified destination\nUsage: python main.py unpack archive destination [file(s)]\n',
    "help": 'Gives information about command usage\nUsage: python main.py help (command)\n',
}

def is_archive(filename: str) -> bool:
    """Tests whether a file is an archive.

    Args:
        filename (str): File path

    Returns:
        True if file exists and ends with .pk
        False otherwise
    """

    return filename.endswith('.pk') and os.path.isfile(filename)

def extract_files(archive_path: str, destination: str, files: list[str] = None) -> None:
    """Extracts a list of files from an archive to a specified destination.

    Args:
        archive_path (str): Path to the archive
        destination (str): Destination path
        files (list[str]): The file names from the headers in the archive of the files to be extracted.
                            If None is provided, the archive is unpacked fully.

    Raises:
        ValueError: If an error occurs while writing to destination"""

    with open(archive_path, "rb") as archive:
        while True:
            header = archive.read(264)
            if not header:
                break

            file_name = header[:256].rstrip(b'\x00').decode('utf-8')

            file_size = int(header[256:264].decode('utf-8'))
            chunk_size = 1024
            output_path = os.path.join(destination, file_name)

            if files and file_name not in files:
                archive.seek(file_size, 1)
                continue

            # will overwrite existing files
            with open(output_path, 'wb') as output_file:
                remaining_bytes = file_size
                while remaining_bytes > 0:
                    chunk = archive.read(min(chunk_size, remaining_bytes))
                    if not chunk:
                        raise ValueError(f"Unexpected end of file when reading {file_name}")
                    output_file.write(chunk)
                    remaining_bytes -= len(chunk)
            print(f"Extracted: {file_name} ({file_size} bytes) to {output_path}")

def get_headers(archive_path: str) -> list[(str, int)]:
    """Extracts all headers from an archive.

    Args:
        archive_path (str): Path to the archive

    Returns:
        list[(str, int)]: List of (filename, filesize) tuples
        """

    headers = []

    with open(archive_path, "rb") as archive:
        while True:
            header = archive.read(264)
            if not header:
                break

            file_name = header[:256].rstrip(b'\x00').decode('utf-8')

            file_size = int(header[256:264].decode('utf-8'))
            headers.append((file_name, file_size))

            archive.seek(file_size, 1)

    return headers

def create_archive(args: list[str]) -> None:
    """Creates an archive.

    Args:
        args (list[str]): List of arguments
            args[0]: main.py
            args[1]: create_archive
            args[2]: destination
            args[3]: archive name
            args[4:]: either a list of files OR a single directory

    Raises:
        ValueError:
            If the destination is not a directory
            If the archive already exists
            If the arguments are not either all files or a single directory
            If a file's name exceeds 256 characters
    """
    if not os.path.isdir(args[2]):
        raise ValueError("Destination must be a directory\n")
    if os.path.isfile(os.path.join(args[2], args[3] + '.pk')):
        raise ValueError("Name already exists\n")
    if not (os.path.isdir(args[4]) and len(args) == 5 or all(os.path.isfile(file) for file in args[4:])):
        raise ValueError("Arguments must be either a list of files or a single directory\n")

    with open(os.path.join(args[2], args[3] + '.pk'), 'wb') as archive:
        #if destination is a directory extract all the files from it
        target_files = []
        if os.path.isdir(args[4]):
            for root, dirs, files in os.walk(args[4]):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.startswith('.'):
                        target_files.append(os.path.join(root, file))

        else:
            target_files += args[4:]

        for file_path in target_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            size_str = f"{file_size:08d}"

            if len(file_name) > 256:
                raise ValueError(f"File name '{file_name}' exceeds 256 characters and cannot fit in the header\n")

            header = file_name.encode('utf-8').ljust(256, b'\x00')  # File name padded to 256 bytes
            header += size_str.encode('utf-8')  # File size (8 bytes, big-endian)

            archive.write(header)

            with open(file_path, "rb") as input_file:
                while chunk := input_file.read(1024):  # Read in chunks to handle large files
                    archive.write(chunk)
            input_file.close()

        archive.close()

def list_content(args: list[str]) -> None:
    """Lists the contents of an archive.

    Args:
        args (list[str]): List of arguments
            args[0]: main.py
            args[1]: list_content
            args[2]: archive path

    Raises:
        ValueError:
            If the archive path does not end with .pk
            If the file does not exist
            If the sum of the size of the files in the archive and the headers does not match the archive size
        """

    archive_path = args[2]
    if not os.path.isfile(archive_path):
        raise ValueError("Archive does not exist\n")
    if len(archive_path) < 4 or not is_archive(archive_path):
        raise ValueError("Archive must end with .pk\n")

    headers = get_headers(archive_path)

    if sum(header[1] for header in headers) + 264 * len(headers) != os.path.getsize(archive_path):
        raise ValueError("Corrupted archive. File Headers don't match file contents.\n")

    print("File names and sizes:")
    for (name, size) in headers:
        print(name, ":", size)

def full_unpack(args: list[str]) -> None:
    """Fully unpacks an archive.

    Args:
         args (list[str]): List of arguments
            args[0]: main.py
            args[1]: full_unpack
            args[2]: archive path
            args[3]: destination

    Raises:
        ValueError:
            If the archive doesn't end with .pk or doesn't exist
            If the destination is not a directory
    """

    if not is_archive(args[2]) and not os.path.isdir(args[3]):
        raise ValueError("Parameters must be an archive and a destination directory.\n")

    extract_files(args[2], args[3])

def unpack(args: list[str]) -> None:
    """Unpacks specified files from an archive to a destination.

    Args:
        args (list[str]): List of arguments
            args[0]: main.py
            args[1]: unpack
            args[2]: archive path
            args[3]: destination
            args[4:]: file names to be unpacked

    Raises:
        ValueError:
            If the archive doesn't end with .pk or doesn't exist
            If the destination is not a directory
            If the specified file names do not exist in the archive
    """

    if not is_archive(args[2]) and not os.path.isdir(args[3]):
        raise ValueError("Parameters must be an archive and a destination directory followed by a list of file names.\n")

    file_names, _ = get_headers(args[2])
    for file_name in args[4:]:
        if file_name not in file_names:
            raise ValueError(f"File '{file_name}' is not in the archive.\n")

    extract_files(args[2], args[3], args[4:])

def help(args: list[str]) -> None:
    """Prints informative messages.

    Args:
        args (list[str]): List of arguments
            args[0]: main.py
            args[1]: help
            args[2]: command (optional)

    Raises:
        ValueError: If the command is not recognized
    """

    if len(args) == 2:
        print("Available commands:\n" + f"{' '.join(comms_to_desc.keys())}\n")
        return

    if args[2] not in comms_to_desc:
        raise ValueError(f"Unknown command: {args[2]}\nUse \'help\' to see available commands\n")
    print(comms_to_desc[args[2]])

def is_valid(args: list[str]) -> bool:
    """Checks whether a command is available and called with the right number of arguments.

    Args:
        args (list[str]): List of arguments
            args[0]: main.py
            args[1]: command

    Returns:
        True if the command is valid
        False otherwise
    """
    if len(args) < 2:
        return False
    elif args[1] == 'create_archive':
        return len(args) >= 5
    elif args[1] == 'list_content':
        return len(args) == 3
    elif args[1] == 'full_unpack':
        return len(args) == 4
    elif args[1] == 'unpack':
        return len(args) >= 5
    elif args[1] == 'help':
        return 2 <= len(args) <= 3
    else:
        return False

comms_to_func = {
    "create_archive": create_archive,
    "list_content": list_content,
    "full_unpack": full_unpack,
    "unpack": unpack,
    "help": help,
}

if __name__ == "__main__":
    if is_valid(sys.argv):
        comms_to_func[sys.argv[1]](sys.argv)
    else:
        if len(sys.argv) > 1 and sys.argv[1] in comms_to_desc.keys():
            raise ValueError(f"\'{sys.argv[1]}\' command misused. Correct usage:\n{comms_to_desc[sys.argv[1]]}")
        else:
            raise ValueError("Invalid command. Use \'help\' command to check available commands.\n")