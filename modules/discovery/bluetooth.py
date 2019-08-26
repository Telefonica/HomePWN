from modules._module import Module
from utils.custom_print import print_info
from bluetooth import discover_devices
from utils.check_root import is_root
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery Bluetooth ",
                       "Description": "Launch this module to discover nearby devices with Bluetooth active.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"timeout": Option.create(name="timeout", value=8, required=True)}
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        print("Searching devices...")
        duration = int(self.args["timeout"])
        devices = discover_devices(
                duration=duration, lookup_names=True, flush_cache=True, lookup_class=True)
        msg = f"found {len(devices)} devices"
        print_info(msg)
        print("-"*len(msg))
        for addr, name, cl in devices:
            try:
                print_info(f"{addr} - {name}  ({hex(cl)})")
            except UnicodeEncodeError:
                print_info(f"{addr} - {name.encode('utf-8', 'replace')}  ({hex(cl)})")