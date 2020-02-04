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
                       "Description": "Running this module you will be able to receive notifications when you write certain charactersitic",
                       "privileges": "root",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?

        options = {"bmac": Option.create(name="bmac", required=True),
                   "type": Option.create(name="type", value="random", required=True, description='Type of device addr'),
                   "uuid-subscribe": Option.create(name="uuid",  required=True, description='Specific UUID for the subscribe characteristic'),
                   "uuid-write": Option.create(name="uuid",  required=True, description='Specific UUID for the write characteristic'),
                   "data": Option.create(name="data", value="Test", required=True, description="Data to write"),
                   "encode": Option.create(name="encode",  required=True, description='Choose data encode'),
                   "iface": Option.create(name="iface", value=0, description='Ble iface index (default to 0 for hci0)')
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
        #new_process_function(self._subscribe, name="Subscribe_ble")
        self._subscribe()


    def _subscribe(self):
        #print_info(f"Trying to subscribe to {self.args['bmac']}")
        device = self.args["bmac"]
        data = self._transform_data(self.args["encode"], self.args["data"])
        type = self.args["type"]
        uuid_subscribe = self.args["uuid-subscribe"]
        uuid_write = self.args["uuid-write"]
        subs = False
        try:
            iface = int(self.args["iface"])
        except:
            iface = 0
        print_info(f"\nTrying to subscribe to {device}")
        ble_device = BLE(device, type, iface)
        
        for x in range(0, 6):
            try:
                ble_device.connect()
                print_ok("\nDevice connected...")
                ble_device.set_delegate(HomeSecurityDelegate)
                ble_device.set_subscribe(uuid_subscribe)
                subs = True
                break
            except KeyboardInterrupt:
                print("Module Interrupted")
                break
            except:
                sleep(3)
        
        ble_device.write_data(data, uuid_write)
        if subs:
            while True:
                try:
                    if(ble_device.device.waitForNotifications(8.0)):
                        break
                    sleep(3)
                except KeyboardInterrupt:
                    print("Module Interrupted")
                    return True
                except:
                    ble_device.disconnect()
                

        print("")
        if subs:
            print_error(f"Unsubscribed {device}")
        else:
            print_error(f"Unable to subscribe to {device}")


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
        print_info(f"A Notification was received from {cHandle}: ")
        print_info(f"|_ Hex: {binascii.b2a_hex(data)}")
        print_info(f"|_ Ascii: {data.decode('utf-8')}")

