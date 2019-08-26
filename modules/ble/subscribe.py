from bluepy.btle import DefaultDelegate
from utils.ble import BLE
import binascii
from time import sleep
from modules._module import Module
from utils.custom_print import print_ok, print_error, print_info
from utils.check_root import is_root
from utils.custom_thread import new_process_function
from utils.shell_options import ShellOptions
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "BLE subscribe",
                       "Description": "Running this module you will be able to receive notifications of a certain BLE device.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {
            'bmac': [None, 'Device address', True],
            'type': ["random", "Device addr type", True]
        }

        options = {"bmac": Option.create(name="bmac", required=True),
                   "type": Option.create(name="type", value="random", required=True, description='Device addr type'),
                   "uuid": Option.create(name="uuid",  required=True, description='Specific UUID for a characteristic'),
                   "data": Option.create(name="data", value="Test", required=True, description="Data to write"),
                   "encode": Option.create(name="encode",  required=True, description='Choose data encode')
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)
    
    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("type", ["random", "public"])
        s_options.add_set_option_values("encode", ["ascii", "hex"])

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        new_process_function(self._subscribe, name="Subscribe_ble")


    def _subscribe(self):
        #print_info(f"Trying to subscribe to {self.args['bmac']}")
        bmac = self.args["bmac"]
        data = self._transform_data(self.args["encode"], self.args["data"])
        subs = False
        conn = 0
        print_info(f"\nTrying to subscribe to {bmac}")
        ble_device = BLE(self.args["bmac"], self.args["type"])
        while True:
            wait = False
            try:
                ble_device.connect()
                print_ok("\nDevice connected...")
                ble_device.write_data(data, self.args["uuid"])
                subs = True
                wait = True
                ble_device.set_delegate(HomeSecurityDelegate)
            except KeyboardInterrupt:
                print("Module Interrupted")
                break
            except:
                sleep(3)
                conn += 1
                if conn == 5:
                    break
                continue

            if wait:
                ble_device.subscribe()


        print("")
        if subs:
            print_error(f"Unsubscribed {self.args['bmac']}")
        else:
            print_error(f"Unable to subscribe to {self.args['bmac']}")


    def _transform_data(self, encode, data):
        if encode == "hex":
            try:
                data = bytes.fromhex(data.replace("0x",""))
            except:
                print_error("Bad Hexadecimal value check it")
                data = None 
        else:
            data = data.encode()
        return data
        
class HomeSecurityDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print_info(f"A Notification was received from {cHandle}: {binascii.b2a_hex(data)}")