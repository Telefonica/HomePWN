from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info
from utils.check_root import is_root
from utils.monitor import Sniffing
from utildata.mac_vendors import mac_devices
from utils.shell_options import ShellOptions
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Wifi Sniffing",
                       "Description": "With this module you can discover stations connected to access points by sniffing. It allows you search for specific venedores devices.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"iface": Option.create(name="iface", required=True),
                   "channel": Option.create(name="channel"),
                   "vendor":  Option.create(name="vendor", description="Configure filter vendor")}

        self.ap_dict = {}
        self.station_dict = {}
        self.F_bssids = []
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("vendor", list(mac_devices.keys()))

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        dev = mac_devices.get(str(self.args["vendor"]), None)
        if dev:
            dev = dev["macs"]
        print_info("Use CTRL^C to end this task")
        sn = Sniffing(iface=self.args["iface"], channel=self.args["channel"], show_aps=False, filter_macs=dev)
        sn.start_sniffing()