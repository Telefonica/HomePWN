from getpass import getpass
from time import sleep
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
from utils.mitmAP import launch_ap
from utils.custom_thread import new_process_function


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Announces a new xiaomi device",
                       "Description": "Announces a new xiaomi device. The device will appear in the nearby devices area of the My Home application (Android only).",
                       "Author": "@josueencinar, @lucferbux"
                       }

        # -----------name-----default_value--description--required?
        options = {"ap_iface": Option.create(name="ap_iface", description="The name of your wireless interface (for the AP)", required=True),
                   "net_iface": Option.create(name="net_iface", description="The name of your internet connected interface", required=True),
                   "device":   Option.create(name="device", description="xiaomi device to be announced", required=True)
                   }

        self.devices = {
            "led-desktop": "yeelink-light-lamp1_miap3c31",
            "roborock-vacuum-s6": "roborock-vacuum-s6_miap023C",
            "led-smart-bulb": "yeelink-light-color3_miapc646",
            "gateway-noeu": "lumi-gateway-v3_miapb0a5",
            "gateway-eu":  "lumi-gateway-mieu01_miio9497",
            "repeater-2": "xiaomi-repeater-v2_miap405a",
            "repeater-pro": "xiaomi-repeater-v3_miapc50c",
            "air-purifier-2": "zhimi-airpurifier-m1_miap672b",
            "cooker": "chunmi-cooker-normal2_miapb74c",
            "smart-socket-wifi-m1-noeu": "chuangmi-plug-m1_miap90d5",
        }
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)


    # Autocomplete set option with values    
    def update_complete_set(self):
        opts = list(self.devices.keys())
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("device", opts)

    # This module must be always implemented, it is called by the run option
    def run(self):
        print_info(f"Xiamoi {self.args['device']} Advertisement...")
        new_process_function(self.setup_ap, name=f"AP_{self.args.get('ssid')}", seconds_to_wait=4)
        seconds = 12
        print_info(f"Wait {seconds} seconds")
        sleep(seconds)
   
    def setup_ap(self):
        ssid = self.devices.get(self.args["device"], None)
        if ssid:
            launch_ap(self.args.get("ap_iface"), self.args.get("net_iface"), "6", True,
                    False, "12345678", False, ssid,
                    False, self.args.get("tshark", False), False, [], "no")
        else:
            print_error("No valid device")