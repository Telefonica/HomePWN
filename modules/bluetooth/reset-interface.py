from subprocess import Popen, PIPE
from modules._module import Module
from utils.custom_print import print_ok, print_info, print_error
from utils.check_root import is_root
from utildata.dataset_options import Option



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Reset a bluetooth interface",
                       "Description": "Launch this module to reset a specific bluetooth interface using hciconfig",
                       "Author": "@josueencinar",
                       "privileges": "root",}

        # -----------name-----default_value--description--required?
        options = {"iface": Option.create(name="iface", required=True, value="hci0")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        proc = Popen(f"hciconfig {self.args['iface']} reset".split(" "), stdout=PIPE, stderr=PIPE)
        data =  proc.communicate()
        if len(data[1]) > 0:
            print_error(data[1].decode().strip())
        else:
            print_ok(f"{self.args['iface']} has been reset")