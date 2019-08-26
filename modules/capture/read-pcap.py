from signal import SIGINT, signal
from prompt_toolkit import print_formatted_text, HTML
from scapy.all import *
import readchar
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utils.custom_thread import new_process_function
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Read pcap",
                       "Description": "This module allows read captured packets from a .pacp file.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?

        options = {"file": Option.create(name="file", value="./files/blueScapy.pcap", required=True, description='pcap file to read'),
                   "pkts": Option.create(name="pkts", value=0, description='Limit total packets to show in terminal (0 no limit)')}
        conf.verb = 0

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        if VERSION <= "2.4.2":
            print_error("You need a 2.4.3 or higher version of scapy")
            return
        packets = rdpcap(self.args["file"])
        limit = 0
        try:
            limit = int(self.args["pkts"])
        except:
            pass
        print("")
        if limit > 0:
            self._show_range_packets(packets, limit)
        else:
            self._show_all_packets(packets)

    def _show_range_packets(self, packets, limit):
        msg = "--show more-- (press q to exit)"
        
        count = 0
        for p in packets:
            count += 1
            if count == limit:
                count = 0
                print_formatted_text(HTML(f"<jj bg='ansiyellow'>{msg}</jj>"), end="")
                res = readchar.readchar()
                # Deletes the last line
                print("\033[A")
                print(" "*len(msg))
                print("\033[A")
                if res.lower() == "q":
                    print("")
                    return
            p.show()

    def _show_all_packets(self, packets):
        for p in packets:
            p.show()