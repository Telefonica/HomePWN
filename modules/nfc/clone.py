# Adapting script from https://nfcpy.readthedocs.io/en/latest/
# Thanks to nehpetsde
# Author: @lucferbux
from modules._module import Module
from utils.custom_print import print_info, print_ok, print_error, print_body
from utils.check_root import is_root
from utildata.dataset_options import Option
from modules.nfc.load import HomeModule as Load
from modules.nfc.dump import HomeModule as Dump


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Clone NFC file",
                       "Description": "This module dumps the contents of an nfc tag in a file and then load this content in a new nfc tag.",
                       "privileges": "root",
                       "OS": "Linux",
                       "Reference" : "https://nfcpy.readthedocs.io/en/latest/",
                       "Author": "@lucferbux, @josueencinar"}

        options = {
            'reader': Option.create(name="reader", value="usb", required=True, description="reader used to write the tag"),
            'file': Option.create(name="file", value="tag.ndef", required=True, description="destination file to dump the content and then load it"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_root
    def run(self):
        dump = Dump()
        load = Load()
        reader_v = ["reader", self.args["reader"]]
        file_v = ["file", self.args["file"]]
        input("Press any key to dump data from a NFC file")
        print_info("Setting dump options")
        dump.set_value(reader_v)
        dump.set_value(file_v)
        dump.run()
        input("Change NFC file and press any key to load the content")
        print_info("Setting load options")
        load.set_value(reader_v)
        load.set_value(file_v)
        load.run()
        print_ok("Done!")