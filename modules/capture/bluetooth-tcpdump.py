from modules._module import Module
from utils.custom_print import print_info
from utils.custom_thread import new_process_command
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Capture Bluetooth Packets ",
                       "Description": "This module run in background and launch tcpdump to capture Bluetooth Packets. When you finish the taks the module save the content in a .pcap.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"file": Option.create(name="file", value="./files/tcpdump.pcap", required=True),
                   "iface": Option.create(name="iface", value="bluetooth0", required=True)}



        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self): 
        command = f"tcpdump -i {self.args['iface']} -w {self.args['file']}"
        new_process_command(command, "tcpdump")