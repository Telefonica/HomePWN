from signal import SIGINT, signal
from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utils.custom_thread import new_process_function
from utils.check_root import is_root
from utildata.dataset_options import Option
conf.verb = 0

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Capture Bluetooth Packets ",
                       "Description": "This module creates a task in background who takes care of capturing Bluetooth Packets with Scapy. When the user finishes the task he saves the packages in a .pcap file.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"file": Option.create(name="file", value="./files/blueScapy.pcap", required=True),
                   "iface": Option.create(name="iface", value="0", required=True, description='Bluetooth interface (Example: set 0 to hci0')}
        conf.verb = 0

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        if VERSION <= "2.4.2":
            print_error("You need a 2.4.3 or higher version of scapy")
            return
        try:
            int(self.args["iface"]) 
        except:
            print_error("iface must be an integer... check your interface with hciconfig")
            return
        print_info("Starting to capture Bluetooth packets")
        new_process_function(self._start_capture, name="blueScapy", seconds_to_wait=1)

    def _start_capture(self):
        bt = BluetoothHCISocket(0)
        pkts = bt.sniff()
        total = len(pkts)
        if not total:
            print_info("No packets captured")
            return
        print_info(f"Writing {total} packets in {self.args['file']}")
        wrpcap(self.args["file"], pkts)
        print_ok("Done!")