from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info, print_error, print_msg
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        conf.verb = 0
        conf.L3socket=L3RawSocket
        information = {"Name": "ARP Scan",
                       "Description": "The module performs an ARP scanner to detect active hosts on a network.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?


        options = {"rhost": Option.create(name="rhost", required=True, description="Hosts to check (Examples: 192.168.56.1 or 192.168.56.0/16)"),
                   "iface": Option.create(name="iface", required=True),
                   "timeout": Option.create(name="timeout", value=2),
                   "verbose": Option.create(name="verbose", value=False)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try:
            if self.args["timeout"]:
                self.args["timeout"] = int(self.args["timeout"])
            else:
                self.args["timeout"] = 2
        except:
            self.args["timeout"] = 2
        if str(self.args["verbose"]).lower() == "true":
            self.args["verbose"] = True
        else:
            self.args["verbose"] = False
	    
        print("Scanning...")
        results = srp(Ether(dst="FF:FF:FF:FF:FF:FF")/ARP(pdst=self.args["rhost"]),timeout=self.args["timeout"], \
                    iface=self.args["iface"],inter=0.1, verbose=self.args["verbose"])[0]
        
        msg = "Hosts alive"
        print(msg)
        print(len(msg)*"-")
        for result in results:
	        print_info(f'MAC: {result[1].hwsrc} - IP: {result[1].psrc}')
