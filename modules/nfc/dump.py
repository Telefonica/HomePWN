# Adapting script from https://nfcpy.readthedocs.io/en/latest/
# Thanks to nehpetsde
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok, print_error, print_body
from utils.check_root import is_root
from utildata.dataset_options import Option
from time import sleep
from nfc.clf import RemoteTarget
import ndef
import nfc


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Dump NFC file",
                       "Description": "This module dumps the contents of an nfc tag in a file. ",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'file': Option.create(name="file", value="tag.ndef", required=True, description="destination file"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        file = self.args.get("file", "tag.ndef")
        reader = self.args.get("reader", "usb")
        path = f"./files/{file}"
        self.write_record(path, reader)

    def write_record(self, path, reader):
        with nfc.ContactlessFrontend(reader) as clf:
            target = clf.sense(RemoteTarget('106A'), RemoteTarget(
                '106B'), RemoteTarget('212F'))
            if target is None:
                print("Waiting for tag...")
            while True:
                target = clf.sense(RemoteTarget('106A'), RemoteTarget(
                    '106B'), RemoteTarget('212F'))
                if target is None:
                    sleep(0.1)  # don't burn the CPU
                    continue

                tag = nfc.tag.activate(clf, target)
                self.dump_tag(tag, path)
                break

    def dump_tag(self, tag, path):
        if not tag.ndef:
            print_error("Some proble ocurred")
            return
        data = tag.ndef.octets
        with open(path, 'wb') as f:
            f.write(data)
            print("File generated")
