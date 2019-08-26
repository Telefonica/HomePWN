# Adapting script from https://nfcpy.readthedocs.io/en/latest/
# Thanks to nehpetsde
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_error, print_msg
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
from utils.check_root import is_root
from time import sleep
from nfc.clf import RemoteTarget
import ndef
import nfc


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Write NFC",
                       "Description": "Use this module to write data to an NFC tag in a custom way.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?
        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'ndef_type': Option.create(name="ndef_type", value="text", required=True, description="type of ndef reg [text | uri | smartposter]"),
            'data': Option.create(name="data", value="", required=True, description="data to write"),
            'append': Option.create(name="append", value=False, required=True, description="overwrite the records of a tag"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("ndef_type", ["text", "uri", "smartposter"])

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        ndef_types = {
            'text': self.set_text_record,
            'uri': self.set_uri_record,
            'smartposter': self.set_smartposter_record
        }
        reader = self.args.get("reader", "usb")
        ndef_type = self.args.get("ndef_type", "text")
        data = self.args.get("data", "")
        append = str(self.args.get("append", "False")).lower() == "true"
        record_type = ndef_types.get(ndef_type, self.set_text_record)

        self.write_record(record_type, reader=reader, data=data, append=append)

    def write_record(self, record_type, reader="usb", data="", append=False):
        """Writes a record in the NDEF format with a given reader
        
        Args:
            record_type ([type]): Type of record (text, uri or smartposter)
            reader (str, optional): Name of the reader you want to use. Defaults to "usb".
            data (str, optional): Data to record. Defaults to "".
            append (bool, optional): Wether the data is appended or overwritten. Defaults to False.
        """
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
                print("Tag found, writting record...")
                record = record_type(data)

                if(append):
                    records = tag.ndef.records
                    print(records)
                    records.append(record)
                    tag.ndef.records = records
                else:
                    tag.ndef.records = [record]

                print("Done")
                break

    def set_text_record(self, data):
        return ndef.TextRecord(data)

    def set_uri_record(self, data):
        return ndef.UriRecord(data)

    def set_smartposter_record(self, data):
        record = ndef.SmartposterRecord(data)
        record.set_title('Home Security', 'en')
        record.resource_type = 'text/html'
        record.action = 'exec'
        return record
