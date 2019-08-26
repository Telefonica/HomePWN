import importlib
from utils.custom_print import print_error, print_info, print_ok
from utils.custom_exception import exception

#@exception("Error importing the module")
def load_module(path):
    """Custom function to load a new module
    
    Args:
        path (str): Path fo the module
    
    Returns:
        HomeModule: Module loaded
    """
    print_info('Loading module...')
    my_path = path.replace("/", ".")
    my_path = "modules." + my_path
    module = importlib.import_module(my_path)
    print_ok('Module loaded!')
    return module.HomeModule()
