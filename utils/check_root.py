from os import getuid
from utils.custom_print import print_error

def is_root():
    if getuid() != 0:
        print_error("To run this service it's necessary to have root privileges")
        return False
    return True