# Adapting script from https://github.com/hexway/apple_bleee
# Thanks to Dmitry Chastuhin @_chipik and https://hexway.io 
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok, print_error, print_body
from utils.check_root import is_root
from utils.ble_apple.ble_utils import Ble_Apple_Utils
from utils.ble_apple.npyscreen_utils import App
from utils.ble_apple.wireless_interface import BadInterfaceException, ModeMonitorException, OwlException, check_wifi_config
from utildata.dataset_options import Option
from utildata.apple_ble_states import phone_states, airpods_states, devices_models, ble_packets_types
from utils.bluetooth_utils import (toggle_device)
from time import sleep
import sys
import json
import urllib3
import requests
import argparse
import multiprocessing
import time
import os
import signal
from os import path
from threading import Thread, Timer





class HomeModule(Module):

    def __init__(self):
        information = {"Name": "BLE Read State",
                       "Description": "This script sniffs BLE traffic and displays status messages from Apple devices. Moreover, the tool detects request for password sharing from apple devices ir order to guess the original phone number",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://github.com/hexway/apple_bleee",
                       "Author": "@lucferbux"}

        options = {
            'ssid': Option.create(name="ssid", value=False, description="Get SSID from requests"),
            'airdrop': Option.create(name="airdrop", value=False, description="Get info from AWDL"),
            'ttl': Option.create(name="ttl", value=10, description="ttl"),
            "iface": Option.create(name="iface", value="wlan0", description="Wireless Interface to enable monitor mode"),
            "hci": Option.create(name="hci", value=0, description="Bluetooth Interface"),
        }
        self.pr = None
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    @is_root
    def run(self):
        ssid = str(self.args.get("ssid", "False")).lower() == "true"
        airdrop = str(self.args.get("airdrop", "False")).lower() == "true"
        ttl = int(self.args.get("ttl", 10))
        iwdev = str(self.args.get("iface", "wlan0"))
        dev_id = int(self.args.get("hci", 0))
        toggle_device(dev_id, True)
        self.pr = multiprocessing.Process(target=self.read_state, 
            args=(ssid, airdrop, ttl, iwdev, dev_id))

        
        try:
            self.pr.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.pr.terminate()
            print(f"Killing {self.pr.pid}")
            os.kill(self.pr.pid, signal.SIGTERM)

    def read_state(self, ssid, airdrop, ttl, iwdev, dev_id):
        """Read the state of the nearby Apple ble devices
        
        Args:
            ssid (Bool): Check to get ssid to phone results
            airdrop (Bool): Check the airdrop to get the phone hash
            ttl (int): Time to live to refresh
            iwdev (str): Wifi interface
            dev_id (int): Bluetooth interface
        """
        ble_utils = Ble_Apple_Utils(ssid, airdrop, ttl, iwdev, dev_id)
        if airdrop:
            try:
                print_info("Configuring owl interface...")
                check_wifi_config(iwdev)
                sleep(1.5) # time to wake up owl process
            except ModeMonitorException:
                print_error("Error, mode monitor not suported in the given interface, press ctr+c to continue")
                return
            except BadInterfaceException:
                print_error("Error, inteface not found, press ctr+c to continue")
                return
            except OwlException:
                print_error("Error, there was a problem setting up owl, press ctr+c to continue, if not insalled --> https://github.com/seemoo-lab/owl.git")
                return
            except Exception as e:
                print_error(f"Error, something went wrong configuring the interface, press ctr+c to continue --> {e}")
                return


        if ssid:
            thread_ssid = Thread(target=ble_utils.get_ssids, args=())
            thread_ssid.daemon = True
            thread_ssid.start()

        

            thread2 = Thread(target=ble_utils.start_listetninig, args=())
            thread2.daemon = True
            thread2.start()

            thread3 = Thread(target=ble_utils.adv_airdrop, args=())
            thread3.daemon = True
            thread3.start()

        ble_utils.init_bluez()
        thread1 = Thread(target=ble_utils.do_sniff, args=(False,))
        thread1.daemon = True
        thread1.start()
        MyApp = App(airdrop, ble_utils)
        MyApp.run()
        thread1.join()

    








