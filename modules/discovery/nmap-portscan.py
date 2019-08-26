try:
    import nmap
    has_nmap = True
except:
    has_nmap = False
from modules._module import Module
from utils.custom_print import print_info, print_error
from utils.check_root import is_root
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "nmap Port scan",
                       "Description": """This module use nmap to perform a port scan. It's possible to perform the following scans:

- S: SYN
- T: Connect
- A: ACK
- W: Window
- M: Maimon
- N: Null
- F: FIN
- X: Xmas """,
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                    "rports": Option.create(name="rports", required=True),
                   "timeout": Option.create(name="timeout", value=6, required=True),
                   "scan": Option.create(name="scan", value="S", 
                                        description='nmap scan. Check namp scans to configure (Examples: SYN = S; Connect = T) ("show info" to check more)', required=True)
                }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        if not has_nmap:
            print_error("To launch this module install nmap (sudo apt install nmap)")
            return
        print("Scanning...")
        nm = nmap.PortScanner()
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 6

        result = nm.scan(self.args["rhost"], self.args["rports"], arguments=f"-s{self.args['scan']} --host-timeout {timeout}")
        try:
            state = result["scan"][self.args["rhost"]]["status"]["state"]
        except:
            state = "down"
        hs = "Host state"
        print("")
        print(hs)
        print("-"*len(hs))
        print_info(state)
        if state == "down":
            return
        ports = result["scan"][self.args["rhost"]]["tcp"]
        msg = "Services found"
        print(msg)
        print("-"*len(msg))
        found = False
        for key, value in ports.items():
            if value["state"] == "open":
                found = True
                print_info(f"{key}  -  {value['name']}")
        if not found:
            print_info("No open ports")