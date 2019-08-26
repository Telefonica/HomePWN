from subprocess import Popen, PIPE
from time import sleep
from typing import cast
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery MDNS Services",
                       "Description": "This module uses avahi to discover certain services via MDNS (Multicast DNS).",
                       "OS": "Linux",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"service": Option.create(name="service", value="_http._tcp", 
                             description='Service type string to search for. (_service._protocol) Set --all to search all services', required=True)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try:
            result = Popen(["avahi-browse", self.args["service"], "--terminate"], stdout=PIPE, stderr=PIPE)
            result.wait()
            error = result.stderr.read()
            if error:
                print_error(error)
                return
            output = result.stdout.readlines()
            for line in output:
                print(line.decode())
        except:
            print_error("Error running avahi-browse")