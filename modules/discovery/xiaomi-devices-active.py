import socket
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Discovery Xiaomi devices ",
                       "Description": "This module uses socket requests to discover Xiaomi devices on a network (Active Discovery). You can configure rhost for a specific search or leave it on None to do a full search.",
                       "Token_info": "Devices with the token all 0 or f are already paired",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--required?--description
        options = {"rhost": Option.create(name="rhost", description="Remote host IP (None to broadcast)"),
                   "timeout": Option.create(name="timeout", value=5)}
        

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        # thanks to python-miio https://github.com/rytilahti/python-miio
        try:
            timeout = int(self.args["timeout"])
        except:
            timeout = 5
        addrs = [] # To avoid duplicates
        if str(self.args["rhost"]) != "None":
            addr = self.args["rhost"]
        else:
            addr = '255.255.255.255'

        print("Sending packets...")
        helobytes = bytes.fromhex('21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 54321))

        while True:
            try:
                data, addr = s.recvfrom(1024)
                token = ""
                try:
                    #TODO
                    token = str(data[16:]).replace("b'","").replace("'","").replace("\\x","")
                except:
                    token = ""
    
                if addr[0] not in addrs:
                    print_info(f"Xiaomi Device >> {addr[0]} - Token({token})")
                    addrs.append(addr[0])
            except socket.timeout:
                print_ok("Discovery done")
                break  
            except Exception as ex:
                print_error(f"Error while reading discover results: {ex}")
                break