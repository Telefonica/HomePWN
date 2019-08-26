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
        information = {"Name": "Write NFC Wifi",
                       "Description": "Write NFC Tag with wifi access point",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?
        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'ssid': Option.create(name="ssid", required=True, description="Network name (Ex. MY_SSID)"),
            'authentication-type': Option.create(name="authentication-type", required=True, description="Network authentication type (Ex. WPA2-Personal)"),
            'encryption-type': Option.create(name="encryption-type",  required=True, description="Network name (Ex. AES)"),
            'network-key': Option.create(name="network-key", required=True, description="Network name (Ex. mypassword)"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)


    # This module must be always implemented, it is called by the run option
    @is_root
    def run(self):
        wifi_attributes = []
        ssid = self.args.get('ssid', "").encode()
        network_key = self.args.get('network-key', "").encode()
        wifi_attributes.append(('ssid', ssid))
        wifi_attributes.append(('authentication-type', self.args.get('authentication-type', "")))
        wifi_attributes.append(('encryption-type', self.args.get('encryption-type', "")))
        wifi_attributes.append(('network-key', network_key))
        self.write_record_wifi(data=wifi_attributes)

    def write_record_wifi(self, reader="usb", data=[]):
        """Writes a wifi record in the NDEF format with a given reader
        
        Args:
            reader (str, optional): Name of the reader you want to use. Defaults to "usb".
            data (list, optional): Data to record. Defaults to empty list.
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
                record = self.format_wifi_tag(data)

                try:
                    tag.ndef.records = [record]
                except:
                    print("Record not written")
                    break

                print("Done")
                break

    def format_wifi_tag(self, data):
        credential = ndef.wifi.Credential()
        credential.set_attribute('network-index', 1)
        try:
            for record in data:
                credential.set_attribute(record[0], record[1])
        except:
            print("Error in attributes")
            raise
        credential.set_attribute('mac-address', b'\xFF\xFF\xFF\xFF\xFF\xFF')
        record = ndef.wifi.WifiSimpleConfigRecord()
        record.name = 'my config token'
        record.set_attribute('credential', credential)
        return record