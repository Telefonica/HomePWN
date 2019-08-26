from scapy.all import *
from modules._module import Module
from utils.custom_print import print_info
from utils.check_root import is_root
from utildata.dataset_options import Option



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Guessing OS through TTL",
                       "Description": "This module checks the TTL to try to find out the operating system. The discovery/nmap-osdetection module is more complete.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                   "timeout": Option.create(name="timeout", value=3)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        print("Checking...\n")
        conf.verb = 0
        conf.L3socket=L3RawSocket
        ip = IP(dst=self.args["rhost"])
        icmp = ICMP()
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 3
        response = sr1(ip/icmp, timeout=timeout)

        if response:
            if response.haslayer(IP):
                msg = "OS Detected: "
                ttl = response.getlayer(IP).ttl
                if ttl == 64:
                    msg += "Linux / MacOS"
                elif ttl == 128:
                    msg += "Windows"
                elif ttl == 255:
                    msg += "FreeBSD / Solaris / SunOS / OpenBSD"
                else:
                    msg += "Unknown"
                print_info(msg)
        else:
            print_info("No response...")     