import sys

def create_archive(args):
    pass

def list_content(args):
    pass

def full_unpack(args):
    pass

def unpack(args):
    pass

def help(args):
    pass

def is_valid(args):
    if len(args) < 2:
        return False
    elif args[1] == 'create_archive':
        return len(args) >= 3
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

comms_to_desc = {
    "create_archive": 'Create an archive\nUsage: python main.py create_archive [file(s)] OR directory\n',
    "list_content": 'List content of archive\nUsage: python main.py list_content archive\n',
    "full_unpack": 'Unpacks all the content of an archive to a specified destination\nUsage: python main.py full_unpack archive destination\n',
    "unpack": 'Unpacks some files of the archive to a specified destination\nUsage: python main.py unpack archive destination [file(s)]\n',
    "help": 'Gives information about command usage\nUsage: python main.py help (command)\n',
}

if __name__ == "__main__":
    if is_valid(sys.argv):
        comms_to_func[sys.argv[1]](sys.argv)
    else:
        if len(sys.argv) > 1 and sys.argv[1] in comms_to_desc.keys():
            print(f"\'{sys.argv[1]}\' command misused. Correct usage:\n" + comms_to_desc[sys.argv[1]])
        else:
            print("Invalid command. Use \'help\' command to check available commands.\n")