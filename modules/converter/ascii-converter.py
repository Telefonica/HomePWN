import binascii
from modules._module import Module
from utils.custom_print import print_ok, print_error, print_info
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Ascii Converter",
                       "Description": "Running this module can convert ascii text to binary and hex",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        # -----------name-----default_value--description--required?

        options = {"ascii": Option.create(name="ascii", required=True),
                   }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)
    

    def run(self):
        ascii_text = self.args["ascii"]
        try:
            binary_text = self.text_to_bits(ascii_text)
            hext_text = ascii_text.encode("utf-8").hex()
            print_info(f"Input -> {ascii_text}")
            print_info(f"|_ Hex: {hext_text}")
            print_info(f"|_ Bin: {binary_text}")
        except:
            print_error("Error processing input")



    def text_to_bits(self, text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

        

