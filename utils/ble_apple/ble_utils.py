import bluetooth._bluetooth as bluez
import hashlib
import subprocess
import time
import re
import os
from threading import Thread, Timer
from utils.opendrop.base import AirDropBase
from utildata.apple_ble_states import phone_states, os_types, airdrop_state_on, airpods_states, devices_models, ble_packets_types, dev_types, dev_sig
from utils.bluetooth_utils import (toggle_device, enable_le_scan, parse_le_advertising_events, disable_le_scan,
                                   raw_packet_to_str, start_le_advertising, stop_le_advertising)


apple_company_id = 'ff4c00'


class Ble_Apple_Utils(object):

    def __init__(self, ssid, airdrop, ttl, dev_id, debug):
        self.airdrop = airdrop
        self.ssid = ssid
        self.dev_id = dev_id  # the bluetooth device is hci0
        self.debug = debug
        self.sock = 0
        self.ttl = ttl
        self.airdropbase = None
        self.phones = {}
        self.resolved_devs = []
        self.resolved_macs = []
        self.resolved_numbers = []
        self.victims = []
        self.dictOfss = {}
        # hash2phone = {}
    
    def le_advertise_packet_handler(self, mac, adv_type, data, rssi):
        """Parse the packet handler
        
        Args:
            mac (str): Mac of the device
            adv_type (str): advertisment type
            data (dict): Dicitonary with the data
            rssi (int): Proximity of the device
        """
        data_str = raw_packet_to_str(data)
        self.read_packet(mac, data_str, rssi)


    def read_packet(self, mac, data_str, rssi):
        """Checks if the bluetooth discovered is an apple divce, get the header and info and transform de data into the display information
        
        Args:
            mac (str): Mac address of the device
            data_str (str): Data converted into string
            rssi (int): Distance estimation of the device
        """
        if apple_company_id in data_str:
            header = data_str[:data_str.find(apple_company_id)]
            data = data_str[data_str.find(apple_company_id) + len(apple_company_id):]
            packet = self.parse_ble_packet(data)
            if ble_packets_types['nearby'] in packet.keys():
                self.parse_nearby(mac, header, rssi, packet[ble_packets_types['nearby']])
            if ble_packets_types['handoff'] in packet.keys():
                self.parse_nandoff(mac, packet[ble_packets_types['handoff']])
            # if ble_packets_types['watch_c'] in packet.keys():
            #     self.parse_watch_c(mac, packet[ble_packets_types['watch_c']])
            if ble_packets_types['wifi_set'] in packet.keys():
                self.parse_wifi_set(mac, packet[ble_packets_types['wifi_set']])
            if ble_packets_types['hotspot'] in packet.keys():
                self.parse_hotspot(mac, packet[ble_packets_types['hotspot']])
            if ble_packets_types['wifi_join'] in packet.keys():
                self.parse_wifi_j(mac, packet[ble_packets_types['wifi_join']])
            if ble_packets_types['airpods'] in packet.keys():
                self.parse_airpods(mac, packet[ble_packets_types['airpods']])
            if ble_packets_types['airdrop'] in packet.keys():
                self.parse_airdrop_r(mac, packet[ble_packets_types['airdrop']])

    def parse_ble_packet(self, data):
        parsed_data = {}
        tag_len = 2
        i = 0
        while i < len(data):
            tag = data[i:i + tag_len]
            val_len = int(data[i + tag_len:i + tag_len + 2], 16)
            value_start_position = i + tag_len + 2
            value_end_position = i + tag_len + 2 + val_len * 2
            parsed_data[tag] = data[value_start_position:value_end_position]
            i = value_end_position
        return parsed_data

    def disable_ble(self):
        disable_le_scan(self.sock)

    def parse_struct(self, data, struct):
        result = {}
        i = 0
        for key in struct:
            if key == 999:
                result[key] = data[i:]
                break
            else:
                size = i + struct[key] * 2
                result[key] = data[i:size]
                i = size
        return result

    

    def get_dict_val(self, dict, key):
        if key in dict:
            return dict[key]
        else:
            return ''

    def init_bluez(self):
        try:
            self.sock = bluez.hci_open_dev(self.dev_id)
        except:
            print(f"Cannot open bluetooth device {self.dev_id}")
            raise

        enable_le_scan(self.sock, filter_duplicates=False)


    def do_sniff(self, prnt):
        try:
            parse_le_advertising_events(self.sock,
                                        handler=self.le_advertise_packet_handler,
                                        debug=False)
        except KeyboardInterrupt:
            pass



    def get_hash(self, data, size=6):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:size]


    def start_listetninig(self):
        self.airdropbase = AirDropBase("find", debug=self.debug)


    def get_airdrop_devices(self):
        """Get the airdrop devices in discovery mode
        
        Returns:
            [airdrop_devices]: List of airdrop devices
        """

        if(self.airdropbase):
            return self.airdropbase.get_devices()
        else:
            return []


    def adv_airdrop(self):

        while True:
            dev_id = self.dev_id
            toggle_device(dev_id, True)
            header = (0x02, 0x01, 0x1a, 0x1b, 0xff, 0x4c, 0x00)
            data1 = (0x05, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01)
            apple_id = (0x00, 0x00)
            phone = (0x00, 0x00)
            email = (0xb7, 0x9b)
            data2 = (0x00, 0x00, 0x00, 0x10, 0x02, 0x0b, 0x00)
            try:
                sock = bluez.hci_open_dev(dev_id)
            except:
                print("Cannot open bluetooth device %i" % dev_id)
                raise
            start_le_advertising(sock, adv_type=0x02, min_interval=500, max_interval=500,
                                data=(header + data1 + apple_id + phone + email + data2))
            time.sleep(10)
            stop_le_advertising(sock)


    def get_airdrop_state(self, result):
        """Check of the status of airdrop
        
        Returns:
            str: Wether the airdrop has been turned on
        """
        if(result in airdrop_state_on):
            return "On"
        else:
            return "Off"

    def refinment_ios_devices(self, status, device):
        """Refinment to get wether the ios device is iPhone or ipad
        
        Args:
            status (str): airdrop status
            device (str): Device
        
        Returns:
            str: Device to get
        """
        ipad = ["47", "4b", "03", "0b", "07"]
        iphone = ["1a", "5b", "5a", "1b", "13", "01", "23", "2b", "27", "5e", "6e", "67", "6b"]
        if(status in iphone):
            return "iPhone"
        elif(status in ipad):
            return "iPad"
        else:
            return "iPhone/iPad"

    def get_operative_system(self, airdrop_code, dev):
        """Parse the struct of the airdrop to get the status
        
        Args:
            airdrop_code (str): airdrop Code
            dev (str): Device
        
        Returns:
            (os, airdrop, device): Tuple with the info about the os, aidrop and device
        """
        if airdrop_code == '1c':
            if dev == 'MacBook':
                return ('macOS', dev)
            else:
                return ('iOS13', dev)
        if airdrop_code == '18':
            if dev == 'MacBook':
                return ('macOS', dev)
            else:
                return ('iOS13', dev)
        if airdrop_code == '14':
            if dev == 'iPhone/iPad':
                return ('iOS', 'Homepod')
        else:
            os = os_types.get(airdrop_code, '<error>')
            return (os, dev)


    # ---------------------- Packet parser ------------------------------------


    def parse_nearby(self, mac, header, rssi, data):
        # 0        1        2                                 5
        # +--------+--------+--------------------------------+
        # |        |        |                                |
        # | status |airdrop |           other                |
        # |        |        |                                |
        # +--------+--------+--------------------------------+
        nearby = {'status': 1, 'airdrop': 1, 'other': 999}

        #{'status': '01', 'airdrop': '98', 'other': '2ac6ce'}
        result = self.parse_struct(data, nearby)
        dev_val = next((value for key, value in dev_sig.items() if key.lower() in header), "<unkown>")
        state = phone_states.get(result['status'], '<unknown>')

        os_state, dev_val = self.get_operative_system(result['airdrop'], dev_val)

        airdrop_state = self.get_airdrop_state(result['status'])
        

        if(os_state == 'WatchOS'):
            dev_val = 'Watch'
            airdrop_state = '-'
            state = '-'
        
        if(dev_val == 'Homepod'):
            state = '-'
            airdrop_state = '-'


        if(dev_val == 'iPhone/iPad'):
            dev_val = self.refinment_ios_devices(result['status'], dev_val)
        
        if mac in self.resolved_macs or mac in self.resolved_devs:
            self.phones[mac]['state'] = state
            self.phones[mac]['airdrop'] = airdrop_state
            self.phones[mac]['os'] = os_state
            self.phones[mac]['time'] = int(time.time())
            self.phones[mac]['device'] = dev_val
            self.phones[mac]['header'] = header
            self.phones[mac]['rssi'] = -abs(rssi)
            self.phones[mac]['data'] = data

        else:
            self.phones[mac] = {'state': "<unkown>", 'device': "<unkown>", 'airdrop': "<unkown>", 'os': "<unkown>", 'rssi': 0, 'time': int(time.time())}
            self.phones[mac]['device'] = dev_val
            self.resolved_macs.append(mac)


    def parse_nandoff(self, mac, data):
        # 0        1                3
        # +--------+----------------+----------------------------+
        # |        |                |
        # |clipbrd | seq.nmbr       |     encr.data
        # |        |                |
        # +--------+----------------+----------------------------+
        handoff = {'clipboard': 1, 's_nbr': 2, 'data': 999}
        result = self.parse_struct(data, handoff)



    # def parse_watch_c(self, mac, data):
    #     print(f"Watch_connection:{data}")


    def parse_wifi_set(self, mac, data):
        # 0                                         4
        # +-----------------------------------------+
        # |                                         |
        # |             iCloud ID                   |
        # |                                         |
        # +-----------------------------------------+
        wifi_set = {'icloudID': 4}
        unkn = '<unknown>'
        if mac in self.resolved_macs or mac in self.resolved_devs:
            self.phones[mac]['state'] = 'WiFi screen'
        else:
            self.phones[mac] = {'state': unkn, 'device': unkn, 'airdrop': unkn, 'os': unkn, 'time': int(time.time())}
            self.resolved_macs.append(mac)


    def parse_hotspot(self, mac, data):
        # 0                2           3            4           5            6
        # +----------------+-----------+------------+-----------+------------+
        # |                |           |            |           |            |
        # |   data1        | battery   |  data2     |cell serv  | cell bars  |
        # |                |           |            |           |            |
        # +----------------+-----------+------------+-----------+------------+
        hotspot = {'data1': 2, 'battery': 1, 'data2': 1, 'cell_srv': 1, 'cell_bars': 1}
        result = self.parse_struct(data, hotspot)
        if mac in self.resolved_macs or mac in self.resolved_devs:
            self.phones[mac]['state'] = '{}.Bat:{}%'.format(self.phones[mac]['state'], int(result['battery'], 16))


    def parse_wifi_j(self, mac, data):
        # 0        1       2                        5                         8                       12                     15                     18
        # +--------+-------+------------------------+-------------------------+-----------------------+----------------------+----------------------+
        # |        |       |                        |                         |                       |                      |                      |
        # | flags  | type  |     auth tag           |     sha(appleID)        |   sha(phone_nbr)      |  sha(email)          |   sha(SSID)          |
        # |        | (0x08)|                        |                         |                       |                      |                      |
        # +--------+--------------------------------+-------------------------+-----------------------+----------------------+----------------------+
        # LUCAS: Not really, it could switch the values and sometimes the apple id is after phone, or email switched with SSID

        wifi_j = {'flags': 1, 'type': 1, 'tag': 3, 'appleID_hash': 3, 'phone_hash': 3, 'email_hash': 3, 'ssid_hash': 3}
        result = self.parse_struct(data, wifi_j)
        id_1 = result.get('appleID_hash', '')
        id_2 = result.get('phone_hash', '')
        if (mac not in self.victims) and (id_1):
            self.victims.append(mac)
            if self.resolved_macs.count(mac):
                self.phones[mac]['hash1'] = id_1
                self.phones[mac]['hash2'] = id_2


    def parse_airpods(self, mac, data):
        # 0                        3        4       5        6       7                 9                                                            25
        # +------------------------+--------+-------+--------+-------+-----------------+------------------------------------------------------------+
        # |                        |        |       |        |       |                 |                                                            |
        # |     some               |state1  |state2 | data1  | data2 |     data3       |             data4                                          |
        # |                        |        |       |        |       |                 |                                                            |
        # +------------------------+--------+-------+--------+-------+-----------------+------------------------------------------------------------+
        airpods = {'some': 3, 'state1': 1, 'state2': 1, 'data1': 1, 'data2': 1, 'data3': 2, 'data4': 16}
        result = self.parse_struct(data, airpods)
        # print("AirPods:{}".format(data))
        # print(result)
        state = unkn = '<unknown>'
        if result['state1'] in airpods_states.keys():
            state = airpods_states[result['state1']]
        else:
            state = unkn
        if result['state2'] == '09':
            state = 'Case:Closed'
        if mac in self.resolved_macs:
            self.phones[mac]['state'] = state
            self.phones[mac]['time'] = int(time.time())
        else:
            self.phones[mac] = {'state': state, 'device': 'AirPods', 'airdrop': '-', 'os': '-',
                        'time': int(time.time())}
            self.resolved_macs.append(mac)


    def parse_airdrop_r(self, mac, data):
        # 0                                         8        9                11                    13                  15                 17       18
        # +-----------------------------------------+--------+----------------+---------------------+-------------------+------------------+--------+
        # |                                         |        |                |                     |                   |                  |        |
        # |           zeros                         |st(0x01)| sha(AppleID)   | sha(phone)          |  sha(email)       |   sha(email2)    |  zero  |
        # |                                         |        |                |                     |                   |                  |        |
        # +-----------------------------------------+--------+----------------+---------------------+-------------------+------------------+--------+
        airdrop_r = {'zeros': 8, 'st': 1, 'appleID_hash': 2, 'phone_hash': 2, 'email_hash': 2, 'email2_hash': 2, 'zero': 1}
        result = self.parse_struct(data, airdrop_r)
