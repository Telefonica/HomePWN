# Adapting script from https://github.com/hexway/apple_bleee
# Thanks to Dmitry Chastuhin @_chipik and https://hexway.io 
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok, print_error, print_body
from utils.check_root import is_root
from utildata.dataset_options import Option
import random
import hashlib
import argparse
from time import sleep
import bluetooth._bluetooth as bluez
from utils.bluetooth_utils import (toggle_device, start_le_advertising, stop_le_advertising)


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Airpods emultaor",
                       "Description": "This script mimics AirPods by sending BLE messages",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://github.com/hexway/apple_bleee",
                       "Author": "@lucferbux"}

        options = {
            'random': Option.create(name="random", value=False, description="Send random charge values"),
            'interval': Option.create(name="inverval", value=10, description="Advertising interval"),
            'ble_iface': Option.create(name="ble_iface", value=0, description="Bluetooth inteface"),
            'left_speaker': Option.create(name="left_speaker", value=0, description="Charge value of left speaker"),
            'right_speaker': Option.create(name="right_speaker", value=0, description="Charge value of right speaker"),
            'case': Option.create(name="case", value=0, description="Charge value of case")
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    @is_root
    def run(self):
        """Get values for the accesories of the airpod and genrates an le advertising with them
        """
        random = str(self.args.get("random", "False")).lower() == "true"
        interval = int(self.args.get("interval", 10))
        dev_id = int(self.args.get("ble_iface", 0))
        if random:
            left_speaker, right_speaker, case = self.random_values()
        else:
            left_speaker = (int(self.args.get("left_speaker", 0)),)
            right_speaker = (int(self.args.get("right_speaker", 0)),)
            case = (int(self.args.get("case", 0)),)

        toggle_device(dev_id, True)

        data1 = (0x1e, 0xff, 0x4c, 0x00, 0x07, 0x19, 0x01, 0x02, 0x20, 0x75, 0xaa, 0x30, 0x01, 0x00, 0x00, 0x45)
        data2 = (0xda, 0x29, 0x58, 0xab, 0x8d, 0x29, 0x40, 0x3d, 0x5c, 0x1b, 0x93, 0x3a)
        try:
            sock = bluez.hci_open_dev(dev_id)
        except:
            print_error("Cannot open bluetooth device %i" % dev_id)
            return
        
        try:
            print_info("Start advertising press ctrl + c to quit...")
            start_le_advertising(sock, adv_type=0x03, min_interval=interval, max_interval=interval,
                                data=(data1 + left_speaker + right_speaker + case + data2))
            while True:
                sleep(2)
        except:
            stop_le_advertising(sock)
            print()
            print_error("Bye")

    def random_values(self):
        """Get random values for all the airpods' accesories
        
        Returns:
            (int, int, int): Tuple with the values of the accesories
        """
        left_speaker = (random.randint(1, 100),)
        right_speaker = (random.randint(1, 100),)
        case = (random.randint(128, 228),)
        return left_speaker, right_speaker, case
