import zeroconf
import ipaddress
from time import sleep
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery Xiaomi devices ",
                       "Description": "The module discovers Xiaomi devices through MDNS. The service type is set to _miio._udp.local.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"timeout": Option.create(name="timeout", value=5, required=True)}
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        listener = Listener()
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 5
        print(f"Searching Xiaomi devices. Timeout: {timeout} seconds")
        browser = zeroconf.ServiceBrowser(zeroconf.Zeroconf(), "_miio._udp.local.", listener)
        sleep(timeout)
        browser.cancel()
        print("")

class Listener:
    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        addr = ipaddress.ip_address(info.address)
        print_info(f"{addr} {info.name} {info.server}")