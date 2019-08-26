from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info
from utils.monitor import Sniffing
from utildata.mac_vendors import mac_devices
from utils.shell_options import ShellOptions
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Search printers",
                       "Description": "Launch this module to discover nearby printers that have a raised access point.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"iface": Option.create(name="iface", required=True, description="Network Interface (that allows promiscuous mode)"),
                   "channel": Option.create(name="channel")}

        self.ap_dict = {}
        self.station_dict = {}
        self.F_bssids = []
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        print_info("Use CTRL^C to end this task")
        printers = ["print", "laserjet", "epson", "deskjet", "officejet" "xerox", "all-in-one", "envy", "scanjet",
                    "pagewide", "ql-"]
        sn = Sniffing(iface=self.args["iface"], channel=self.args["channel"], show_stations=False, filter_name=printers)
        sn.start_sniffing()