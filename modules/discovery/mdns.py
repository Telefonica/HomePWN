import zeroconf
import ipaddress
import readchar
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery MDNS Services",
                       "Description": "With this module certain services can be discovered via MDNS (Multicast DNS).",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"service": Option.create(name="service", value="_http._tcp.local.", 
                                description='Service type string to search for. (_service._protocol)', required=True)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        listener = Listener()
        print("Searching. Press q to stop")
        browser = zeroconf.ServiceBrowser(
            zeroconf.Zeroconf(), self.args["service"], listener)
        key = ""
        while key.lower() != "q":
            key = readchar.readchar()
        browser.cancel()
        print("")

class Listener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        addr = ipaddress.ip_address(info.address)
        print_info(f"{addr} {info.name} {info.server}")