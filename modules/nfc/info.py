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
        information = {"Name": "Show NFC Info",
                       "Description": "Launch this module to show all content contained on an NFC Tag.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'verbose': Option.create(name="verbose", value=False, description="verbose mode"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        reader = self.args.get("reader", "usb")
        verbose = str(self.args.get("verbose", "False")).lower() == "true"
        self.write_record(reader=reader, verbose=verbose)

    def write_record(self, reader="usb", verbose=False):
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
                self.show_tag(tag, verbose)
                break

    def show_tag(self, tag, verbose):
        print(tag)
        if(tag.ndef):
            print_info("NDEF Capabilities:")
            print_body(f"  readable  = {self.get_color(tag.ndef.is_readable)}")
            print_body(
                f"  writeable = {self.get_color(tag.ndef.is_writeable)}")
            print(f"  capacity  = {tag.ndef.capacity} byte")
            print(f"  message   = {tag.ndef.length} byte")
            if tag.ndef.length > 0:
                print_info("NDEF Message:")
                for i, record in enumerate(tag.ndef.records):
                    print_ok(f"record {i + 1}")
                    print("  type =", repr(record.type))
                    print("  name =", repr(record.name))
                    print("  data =", repr(record.data))

        if(verbose):
            print_info("Memory Dump:")
            print('  ' + '\n  '.join(tag.dump()))

    def get_color(self, state):
        if(state):
            return "<ansigreen>yes</ansigreen>"
        else:
            return "<ansired>no</ansired>"
