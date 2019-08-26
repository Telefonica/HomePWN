from subprocess import Popen, PIPE, check_call
from modules._module import Module
from utils.custom_print import print_error, print_info
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Wifi Discover Access Points with nmcli",
                       "Description": "This module allows us to see the access points using nmcli, the command used is: `nmcli dev wifi list`. No configuration required.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = { }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        command = "nmcli dev wifi list"
        try:
            aux = check_call("nmcli", stdout=PIPE)
            data = Popen(command, shell=True, stdout=PIPE).stdout.read()
            i = 1
            for line in data.decode().split("\n"):
                print_info(line)
        except:
            print_error("nimcli not found")