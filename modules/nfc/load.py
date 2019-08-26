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
        information = {"Name": "Load NFC file",
                       "Description": "The module loads the content from a file to an nfc tag.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'file': Option.create(name="file", value="tag.ndef", required=True, description="source file"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        file = self.args.get("file", "tag.ndef")
        reader = self.args.get("reader", "usb")
        path = f"./files/{file}"
        self.load_record(path, reader)

    def load_record(self, path, reader):
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
                self.load_tag(tag, path)
                break

    def load_tag(self, tag, path):

        try:
            f = open(path, 'rb')
        except Exception:
            print_error("file not found")
        else:
            with f:
                data = f.read()
                if tag.ndef is None:
                    print("This is not an NDEF Tag.")
                    return

                if not tag.ndef.is_writeable:
                    print("This Tag is not writeable.")
                    return

                if data == tag.ndef.octets:
                    print("The Tag already contains the message to write.")
                    return

                if len(data) > tag.ndef.capacity:
                    print("The new message exceeds the Tag's capacity.")
                    return

                if tag.ndef.length > 0:
                    print("Old NDEF Message:")
                    for i, record in enumerate(tag.ndef.records):
                        print("record", i + 1)
                        print("  type =", repr(record.type))
                        print("  name =", repr(record.name))
                        print("  data =", repr(record.data))

                tag.ndef.records = list(ndef.message_decoder(data))
                if tag.ndef.length > 0:
                    print("New NDEF Message:")
                    for i, record in enumerate(tag.ndef.records):
                        print("record", i + 1)
                        print("  type =", repr(record.type))
                        print("  name =", repr(record.name))
                        print("  data =", repr(record.data))
