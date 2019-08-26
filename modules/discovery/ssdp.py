import socket
import select
import zeroconf
from datetime import datetime, timedelta
import re
import requests
from xml.etree import cElementTree as ET
from utils.custom_print import  print_msg
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        self.SSDP_MX = 2
        self.SSDP_TARGET = ("239.255.255.250", 1900)
        information = {"Name": "Discovery SSDP Services",
                       "Description": "Using this module you will be able to discover active devices through SSDP protocol.",
                       "Author": "@josueencinar, @pablogonzalezpe",
                       "Reference": "https://github.com/home-assistant/netdisco/blob/master/netdisco/ssdp.py"}

        # -----------name-----default_value--description--required?
        options = {"timeout": Option.create(name="timeout", value=5, required=True),
                   "service": Option.create(name="service", value="ssdp:all", description='Service type string to search for')}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    def _ssdp_request(self, ssdp_st):
        """Return request bytes for given st and mx."""
        return "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'ST: {}'.format(ssdp_st),
            'MX: {:d}'.format(self.SSDP_MX),
            'MAN: "ssdp:discover"',
            'HOST: {}:{}'.format(*self.SSDP_TARGET),
            '', '']).encode('utf-8')

    # This function must be always implemented, it is called by the run option
    def run(self):
        """Send a message over the network to discover uPnP devices.
        Inspired in https://github.com/home-assistant/netdisco/blob/master/netdisco/ssdp.py
        """
        devices = []
        timeout = int(self.args["timeout"])
        ssdp_requests = self._ssdp_request(self.args["service"])
        stop_wait = datetime.now() + timedelta(seconds=timeout)
        sockets = self._get_sockets()

        for sock in [s for s in sockets]:
            try:
                sock.sendto(ssdp_requests, self.SSDP_TARGET)
                sock.setblocking(False)
            except socket.error:
                sockets.remove(sock)
                sock.close()
        try:
            while sockets:
                time_diff = stop_wait - datetime.now()
                seconds_left = time_diff.total_seconds()
                if seconds_left <= 0:
                    break

                ready = select.select(sockets, [], [], seconds_left)[0]

                for sock in ready:
                    try:
                        data, address = sock.recvfrom(1024)
                        response = data.decode("utf-8")
                        data = re.findall("LOCATION: .*", response)
                        for line in data:
                            devices.append(line.split(": ")[1].strip())
                    except UnicodeDecodeError:
                        print_error('Ignoring invalid unicode response from %s', address)
                        continue
                    except socket.error:
                        print_error("Socket error while discovering SSDP devices")
                        sockets.remove(sock)
                        sock.close()
                        continue
        finally:
            for s in sockets:
                s.close()
        
        self._parse_result(devices)
         
    def _get_sockets(self):
        sockets = []
        for addr in zeroconf.get_all_addresses():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Set the time-to-live for messages for local network
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                                self.SSDP_MX)
                sock.bind((addr, 0))
                sockets.append(sock)
            except socket.error:
                pass
        
        return sockets

    def _parse_result(self, devices):
        # avoid duplicates
        my_list = []
        if not devices:
            print_error("No devices found")
        else:
            for device in devices:
                ip = device.replace("http://","").split(":")[0]
                if ip not in my_list:
                    my_list.append(ip)
                    response = requests.get(device)
                    if response.status_code == 200:
                        self._info_extract(response.text, ip)
                        print("")
    
    def _info_extract(self, data, ip):
        search = ["friendlyName", "manufacturer"]
        result = {"ip": ip}
        tree = ET.fromstring(data)

        for t in tree.getiterator():
            tag = t.tag.split("}")[1]
            if tag in search:
                result[tag] = t.text

        self._show_result(result)

    def _show_result(self, result):
        for k, v in result.items():
            print_msg(k, "blue")
            print_msg(f"|_ {v}", "yellow")