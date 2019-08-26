from modules._module import Module
from utils.ble import BLE
from utils.custom_print import print_ok, print_error, print_info
from utils.check_root import is_root
from utils.shell_options import ShellOptions
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "BLE Characteristics",
                       "Description": "This module serves to read all the characteristics of a given BLE device. If you specify a UUID, only that characteristic will be read.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"bmac": Option.create(name="bmac", required=True),
                   "uuid": Option.create(name="uuid", description='Specific UUID for a characteristic'),
                   "type": Option.create(name="type", value="random", required=True, description='Device addr type')
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("type", ["random", "public"])

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        ble_device = BLE(self.args["bmac"], self.args["type"])

        attempt = 1
        success = False
        while attempt <= 5 and not success:
            print_info(f"Trying to connect {self.args['bmac']}. (Attempt: {attempt})")
            try:
                ble_device.connect()
                success = True
            except KeyboardInterrupt:
                print_info("Interrupted... exit run")
                return 
            except:
                attempt += 1

        if not success:
            print_error("Failed to connect")
            return
        
        uuid = self.args["uuid"]
        if uuid:
            ble_device.read_specific_characteristic(uuid)
        else:
            ble_device.read_all_characteristics()
        
        ble_device.disconnect()