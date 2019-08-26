from os import geteuid
from bluetooth import find_service
from modules._module import Module
from utils.custom_print import print_ok, print_info
from utildata.dataset_options import Option



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Bluetooth SDP Services",
                       "Description": "Displays services being advertised on a specified bluetooth device",
                       "Author": "@josueencinar",
                       "privileges": "root",
                       "Reference": "https://github.com/pybluez/pybluez/blob/master/examples/simple/sdp-browse.py"}

        # -----------name-----default_value--description--required?

        options = {"bmac": Option.create(name="bmac", description='Device address (None == all devices)')}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        print_info("Searching services...")
        bmac = self.args["bmac"]
        # User input is String (just in case)
        if str(bmac) == "None":
            print_info("This process can take time, patience")
            bmac = None
        services = find_service(address=bmac)
        if len(services) > 0:
            print_ok(f"Found {len(services)} services")
            print("")
            self._show_services(services)
        else:
            print_info("No services found")

    def _show_services(self, services):
        for svc in services:
            name = svc.get("name")
            if not name:
                name = "Unknown"
            print_info(f"<b>Service Name: <ansigreen>{name}</ansigreen></b>")
            for key in sorted(svc.keys()):
                if key == "name":
                    continue
                value = svc.get(key, None)
                if value:
                    print_info(f"    {key}:  <ansigreen>{value}</ansigreen>")        