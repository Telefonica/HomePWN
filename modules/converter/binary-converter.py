import binascii
from modules._module import Module
from utils.custom_print import print_ok, print_error, print_info
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Binary converter",
                       "Description": "Running this module can convert binary string to ascii and hex",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?

        options = {"binary": Option.create(name="binary", required=True),
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)
    

    def run(self):
        binary_text = self.args["binary"]
        try:
            ascii_text = self.text_from_bits(binary_text)
            hext_text = ascii_text.encode("utf-8").hex()
            print_info(f"Input -> {binary_text}")
            print_info(f"|_ Hex: {hext_text}")
            print_info(f"|_ Ascii: {ascii_text}")
        except Exception as e:
            print(e)
            print_error("Error processing input")



    def text_from_bits(self, bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits, 2)
        return self.int2bytes(n).decode(encoding, errors)

    def int2bytes(self, i):
        hex_string = '%x' % i
        n = len(hex_string)
        return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

        

