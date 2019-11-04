"""
OpenDrop: an open source AirDrop implementation
Copyright (C) 2018  Milan Stute
Copyright (C) 2018  Alexander Heinrich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import time

import ipaddress
import logging
import argparse
import sys
import json
import os
from time import sleep
import threading

from .client import AirDropBrowser, AirDropClient
from .config import AirDropConfig, AirDropReceiverFlags
from .server import AirDropServer
from .error import ReceiverError

logger = logging.getLogger(__name__)


def main():
    AirDropBase(sys.argv[1:])


class AirDropBase:

    def __init__(self, action, callback=None, file=None, debug=False, receiver=None, email=None, phone=None, name=None, model=None, interface=None):
        # parser = argparse.ArgumentParser()
        # parser.add_argument('action', choices=['receive', 'find', 'send'])
        # parser.add_argument('-f', '--file', help='File to be sent')
        # parser.add_argument('-r', '--receiver', help='Peer to send file to (can be index, ID, or hostname)')
        # parser.add_argument('-e', '--email', nargs='*', help='User\'s email addresses (currently unused)')
        # parser.add_argument('-p', '--phone', nargs='*', help='User\'s phone numbers (currently unused)')
        # parser.add_argument('-n', '--name', help='Computer name (displayed in sharing pane)')
        # parser.add_argument('-m', '--model', help='Computer model (displayed in sharing pane)')
        # parser.add_argument('-d', '--debug', help='Enable debug mode', action='store_true')
        # parser.add_argument('-i', '--interface', help='Which AWDL interface to use', default='awdl0')
        # args = parser.parse_args(args)

        if debug:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(name)s: %(message)s')


        # TODO put emails and phone in canonical form (lower case, no '+' sign, etc.)
        self.config = AirDropConfig(email=email, phone=phone,
                                    computer_name=name, host_name=name, computer_model=model,
                                    debug=debug, interface=interface)
        self.server = None
        self.client = None
        self.discover = []
        self.browser = None
        self.sending_started = False
        self.lock = threading.Lock()
        try:
            if action == 'receive':
                self.receive(callback)
            elif action == 'find':
                self.find()
            else:  # action == 'send'
                if file is None or not os.path.isfile(file):
                    raise FileNotFoundError
                self.file = file
                if receiver is None:
                    raise ReceiverError
                self.receiver = receiver
                self.send()
        except KeyboardInterrupt:
            if self.browser is not None:
                self.browser.stop()
            if self.server is not None:
                self.server.stop()

    def find(self):
        logger.info('Looking for receivers. Press enter to stop ...')
        self.browser = AirDropBrowser(self.config)
        self.browser.start(callback_add=self._found_receiver)


    def get_devices(self):
        return self.discover

    def _found_receiver(self, info):
        thread = threading.Thread(target=self._send_discover, args=(info,))
        thread.start()

    def _send_discover(self, info):
        try:
            address = ipaddress.ip_address(info.address).compressed
        except ValueError:
            return  # not a valid address
        id = info.name.split('.')[0]
        hostname = info.server
        port = int(info.port)
        #logger.debug('AirDrop service found: {}, {}:{}, ID {}'.format(hostname, address, port, id))
        client = AirDropClient(self.config, (address, int(port)))
        flags = int(info.properties[b'flags'])
        receiver_name = None
        os_info = "<unknown>"
        if flags & AirDropReceiverFlags.SUPPORTS_DISCOVER_MAYBE:
            try:
                reponse = client.send_discover()
                with open("airdrop_test.txt", "a+") as patata:
                    patata.write(response)
                receiver_name =reponse.get('ReceiverComputerName')
                ReceiverMediaCapabilities = json.loads(reponse['ReceiverMediaCapabilities'])
                os_version = ReceiverMediaCapabilities.get('Vendor', {}).get('com.apple', {}).get('OSVersion', '') 
                os_build_version = ReceiverMediaCapabilities.get('Vendor', {}).get('com.apple', {}).get('OSBuildVersion', '') 
                os_info = "{} ({})".format('.'.join(map(str, os_version)), os_build_version)
            except TimeoutError:
                pass
            except:
                pass

        discoverable = receiver_name is not None

        node_info = {
            'name': receiver_name,
            'address': address,
            'host': hostname,
            'port': port,
            'id': id,
            'flags': flags,
            'discoverable': discoverable,
            'os': os_info,
        }
        self.lock.acquire()
        ids = [dev.get('id', '') for dev in self.discover]
        addresses = [dev.get('address', '') for dev in self.discover]
        if((node_info.get('id', '') not in ids) and (node_info.get('address', '') not in addresses)):
            self.discover.append(node_info)
        # if discoverable:
        #     logger.info('Found  index {}  ID {}  name {}'.format(index, id, receiver_name))
            #print('Found  index {}  ID {}  name {}'.format(index, id, receiver_name))
        # #print (node_info)
        self.lock.release()


    def receive(self, callback):
        self.server = AirDropServer(self.config, callback=callback)
        self.server.start_service()
        self.server.start_server()
        

    def send(self):
        info = self._get_receiver_info()
        if info is None:
            return
        self.client = AirDropClient(self.config, (info['address'], info['port']))
        logger.info('Asking receiver to accept ...')
        if not self.client.send_ask(self.file):
            logger.warning('Receiver declined')
            return
        logger.info('Receiver accepted')
        logger.info('Uploading file ...')
        if not self.client.send_upload(self.file):
            logger.warning('Uploading has failed')
            return
        logger.info('Uploading has been successful')

    def _get_receiver_info(self):
        if not os.path.exists(self.config.discovery_report):
            logger.error('No discovery report exists, please run \'opendrop find\' first')
            return None
        age = time.time() - os.path.getmtime(self.config.discovery_report)
        if age > 60:  # warn if report is older than a minute
            logger.warning('Old discovery report (%.1f seconds), consider running \'opendrop find\' again', age)
        with open(self.config.discovery_report, 'r') as f:
            infos = json.load(f)

        # (1) try 'index'
        try:
            self.receiver = int(self.receiver)
            return infos[self.receiver]
        except ValueError:
            pass
        except IndexError:
            pass
        # (2) try 'id'
        if len(self.receiver) is 12:
            for info in infos:
                if info['id'] == self.receiver:
                    return info
        # (3) try hostname
        for info in infos:
            if info['name'] == self.receiver:
                return info
        # (fail)
        logger.error('Receiver does not exist (check -r,--receiver format or try \'opendrop find\' again')
        return None
