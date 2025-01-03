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

comms_to_func = {
    "create_archive": create_archive,
    "list_content": list_content,
    "full_unpack": full_unpack,
    "unpack": unpack,
    "help": help,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python packster\main.py [COMMAND]")
    else:
        comms_to_func[sys.argv[1]](sys.argv)