
from getpass import getpass
from time import sleep
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
from utils.mitmAP import launch_ap
from utils.custom_thread import new_process_function


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Set up an Access Point",
                       "Description": "This module will be in charge of raising an access point configured with the different options. Allows you to start Wireshark and Tshark to capture traffic automatically.",
                       "Author": "@josueencinar",
                       "Reference": "https://github.com/xdavidhu/mitmAP"}

        # -----------name-----default_value--description--required?
        options = {"ap_iface": Option.create(name="ap_iface", description="The name of your wireless interface (for the AP)", required=True),
                   "net_iface": Option.create(name="net_iface", description="The name of your internet connected interface", required=True),
                   "channel": Option.create(name="channel", description='Network Channel to the AP', value=3, required=True),
                   "sslstrip": Option.create(name="sslstrip", description="Use SSLSTRIP 2.0?", value=True),
                   "hostapd_wpa": Option.create(name="hostapd_wpa", description='Enable WPA2 encryption?', value=True),
                   "wpa_passphrase": Option.create(name="wpa_passphrase", description="Please enter the WPA2 passphrase for the AP ('minimum 8 characters')", value="12345678"),
                   "driftnet": Option.create(name="driftnet", description="Capture unencrypted images with DRIFTNET?", value=False),
                   "ssid": Option.create(name="ssid", description='AP SSID to show', required=True),
                   "wireshark": Option.create(name="wireshark", description='Start Wireshark?', value=False),
                   "tshark": Option.create(name="tshark", description='Capture packets to .pcap with TSHARK? (no gui needed)', value=False),
                   "dnsspoof": Option.create(name="dnsspoof", description='Spoof DNS?', value=False),
                   "proxy": Option.create(name="proxy", description='Capture traffic? (only works with no sslstrip)', value=False)        
                   }
        self.all_dns = {"ssl": [],
                        "no_ssl": []}
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # Autocomplete set option with values    
    def update_complete_set(self):
        opts = ["True", "False"]
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("sslstrip", opts)
        s_options.add_set_option_values("hostapd_wpa", opts)
        s_options.add_set_option_values("driftnet", opts)
        s_options.add_set_option_values("wireshark", opts)
        s_options.add_set_option_values("tshark", opts)
        s_options.add_set_option_values("dnsspoof", opts)
        s_options.add_set_option_values("proxy", ["ssl", "nossl", "no"])

    # This module must be always implemented, it is called by the run option
    def run(self):
        print_info("""
            _ _              ___  ______
           (_) |            / _ \ | ___ \\
  _ __ ___  _| |_ _ __ ___ / /_\ \| |_/ /
 | '_ ` _ \| | __| '_ ` _ \|  _  ||  __/
 | | | | | | | |_| | | | | | | | || |
 |_| |_| |_|_|\__|_| |_| |_\_| |_/\_|
 """)
        print_info("Starting process...")
        if self.args.get("dnsspoof", False):
            dns_num = self.dns()
            i = 0
            while dns_num != i:
                dns_num_temp = i + 1
                dns_domain = input("[?] " + str(dns_num_temp) + ". domain to spoof: ")
                dns_ip = input("[?] Fake IP for domain '" + dns_domain + "': ")
                dns_line_ssl = dns_domain + " " + dns_ip + "\n"
                dns_line_no_ssl = "address=/" + dns_domain + "/" + dns_ip + "\n"
                self.all_dns["ssl"].append(dns_line_ssl)
                self.all_dns["no_ssl"].append(dns_line_no_ssl)
                i = i + 1

        new_process_function(self.setup_ap, name=f"AP_{self.args.get('ssid')}", seconds_to_wait=4)
        seconds = 12
        print_info(f"Wait {seconds} seconds")
        sleep(seconds)

    
    def setup_ap(self):
        try:
            ch = int(self.args.get("chennel", 3))
            if ch > 13:
                raise "Wrong channel"
        except Exception as e:
            print_error(e)
            ch = 3
        
        launch_ap(self.args.get("ap_iface"), self.args.get("net_iface"), str(ch), self.args.get("sslstrip", True),
                  self.args.get("hostapd_wpa", True), self.args.get("hostapdwpa_passphrase_wpa", "12345678"), self.args.get("driftnet", False), self.args.get("ssid"),
                  self.args.get("wireshark", False), self.args.get("tshark", False), self.args.get("dnsspoof", False), self.all_dns, self.args.get("proxy", "no"))

    def dns(self):
        while True:
            ssl_dns_num = input("[?] How many domains do you want to spoof?: ")
            if ssl_dns_num.isdigit():
                return int(ssl_dns_num)
            else:
                print("[!] Please enter a number.")