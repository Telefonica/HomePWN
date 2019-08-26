from modules._module import Module
from utils.custom_print import print_info, print_error
from utils.check_root import is_root
from utils.ble import Scan
from utildata.dataset_options import Option



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery BLE devices ",
                       "Description": "With this module you can discover nearby devices with BLE (Bluetooth Low Energy) active. The result will be sorted by RSSI.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"timeout": Option.create(name="timeout", value=5, required=True),
                   "rssi": Option.create(name="rssi", description='dB signal to filter (min value, example -60)')}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        print("Searching BLE devices...\n")
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 5
        scan = Scan()
        devices = scan.scan_devices(timeout=timeout)
        scan.show_devices(devices, self.args["rssi"])