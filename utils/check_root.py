from os import getuid
from utils.custom_print import print_error

def is_root(func):
    """Decorator used to check if the current tool is in root, if not exist the module
    
    Args:
        func (func): function passed to the decorator
    
    Returns:
        wrapper: decorator wrapped
    """
    def wrapper(*args):
        if getuid() != 0:
            print_error("To run this service it's necessary to have root privileges")
            return
        func(*args)
    return wrapper
