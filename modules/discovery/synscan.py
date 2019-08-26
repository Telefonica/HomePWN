from scapy.all import *
from multiprocessing.dummy import Pool
from modules._module import Module
from utils.custom_print import print_info, print_error, print_msg
from utils.check_root import is_root
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        conf.verb = 0
        conf.L3socket=L3RawSocket
        information = {"Name": "SYN Scan",
                       "Description": "Launches this module to perform a TCP SYN Scan to detect open ports on a system. rport and rports are optional, but at least one option must be configured.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                    "rport": Option.create(name="rport"),
                    "rports": Option.create(name="rports"),
                   "timeout": Option.create(name="timeout", value=2),
                   "verbose": Option.create(name="verbose", value=False)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        try:
            if self.args["timeout"]:
                self.args["timeout"] = int(self.args["timeout"])
            else:
                self.args["timeout"] = 2
        except:
            self.args["timeout"] = 2
        if self.args["rport"]:
            self._scan(int(self.args["rport"]))
        elif self.args["rports"]:
            try:
                first, last = self.args["rports"].split("-")
                ports_list = []
                for port in range(int(first), int(last)+1):
                    ports_list.append(port)
                pool = Pool(4)
                pool.map(self._scan, ports_list)
                pool.close()
                pool.join()
            except:
                print_error("Bad format in rposts")
        else:
            print_info("rport or rports must be configured")

    def _scan(self, dport):
        SYNACK = 0x12
        sport = RandShort()
        try:
            if self.args["timeout"]:
                timeout = int(self.args["timeout"])
            else:
                timeout = 2
        except:
            timeout = 2
        response = sr1(IP(dst=self.args["rhost"])/TCP(sport=sport, dport=dport, flags="S"), timeout=timeout)
        if response and response.getlayer(TCP).flags == SYNACK:
            send(IP(dst=self.args["rhost"])/TCP(sport=sport, dport=dport, flags="R"))
            print_msg(f"{dport} open", color="green")
        elif str(self.args["verbose"]).lower() == "true":
             print_msg(f"{dport} close", color="red")            