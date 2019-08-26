from os import system, environ
from bluetooth import discover_devices
from modules._module import Module
from utils.custom_print import print_ok, print_error, print_info
from utils.check_root import is_root
import modules.bluetooth.launchService as Service
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Bluetooth MAC Spoofing",
                       "Description": "This module is designed to allow you spoof a bluetooth device using Spooftooph. If you want to create a bluetooth service with the features of an active device near you, you must specify the name or bmac to find the device and extract the information. It is also possible to manually specify everything and 'invent' a bluetooth.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@josueencinar",
                       "Reference": "https://github.com/pwnieexpress/pwn_plug_sources/tree/master/src/bluetooth/spooftooph/source"}

        # -----------name-----default_value--description--required?
        options = {"name": Option.create(name="name", description="Device name to spoof"),
                   "iface": Option.create(name="iface", value="hci0", required=True),
                   "bmac": Option.create(name="bmac", description="New device address"),
                   "class": Option.create(name="class",  description='Bluetooth class (Profile)')
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        print_info("Searching bluetooth devices to check MAC...")
        devices  = discover_devices(lookup_names=True, lookup_class=True)
        device_name = None
        device_class = None
        for mac, name, cl in devices:
            if self.args["bmac"] == mac:
                print_info("A nearby device has been found")
                device_name = name
                device_class = hex(cl)
                break

        if not device_name:
            print_info("No nearby device found")
            if self.args['name']:
                device_name = self.args['name']
            else:
                print_error("We can't find the name")
                return

        if not device_class:
            if self.args['class']:
                device_class = self.args['class']
            else:
                print_error("We can't find the profile")
                return
        print_info("Trying to change name and MAC")
        result = system(f"apps/spooftooph -i {self.args['iface']} -a {self.args['bmac']}")
        if int(result) == 0:
            print_ok("Done!")
            print_info("Starting Bluetooth service to allow connections")
            self._start_service(device_name, device_class)
        else:
            print_error("Execution fault...")
            

    def _start_service(self, d_name, d_class):
        service = Service.HomeModule()
        iface = ["iface", self.args['iface']]
        name = ["name", d_name]
        profile = ["class", d_class]
        service.set_value(iface)
        service.set_value(name)
        service.set_value(profile)
        service.run()