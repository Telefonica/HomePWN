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
        information = {"Name": "nmap OS detection",
                       "Description": "This module uses nmap to try to guess the operating system behind an IP.",
                       "privileges": "root",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                   "timeout": Option.create(name="timeout", value=5)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        if not has_nmap:
            print_error("To launch this module install nmap (sudo apt install nmap)")
            return
        print("Trying to get OS")
        nm = nmap.PortScanner()
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 6
        result = nm.scan(self.args["rhost"], arguments=f"-O --host-timeout {timeout}")
        try:
            state = result["scan"][self.args["rhost"]]["status"]["state"]
        except:
            state = "down"
        print_info(f"Host state: <b>{state}</b>")

        try:
            print_info(f'OS: <b>{result["scan"][self.args["rhost"]]["osmatch"][0]["name"]}</b>')
        except:
            print_info("OS not found")