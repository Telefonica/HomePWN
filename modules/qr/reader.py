from modules._module import Module
from utils.custom_print import print_error
from utils.qr_reader import display_qr
from utildata.dataset_options import Option
from pyzbar.pyzbar import decode
from PIL import Image

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "QR Reader",
                       "Description": "This module allows you to read QR codes from a file.",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        options = {
            'file': Option.create(name="file", value="qr.png", required=True, description="source file"),
            'verbose': Option.create(name="verbose", value=False, description="verbose mode"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        verbose = str(self.args.get("verbose", "False")).lower() == "true"
        path = self.args.get("file", "qr.png")
        if("/" not in path):
            path = f"./files/{path}"
        
        self.read_qr(verbose, path)
    
    def read_qr(self, verbose, path):
        """Reads the QR code to get the attributes
        
        Args:
            verbose (Boolean): Set to True to verbose mode
            path (str): Path to store the image
        """
        try:
            read = decode(Image.open(path))
        except:
            print_error("Error, file not found or not readable")
            return
        display_qr(read, verbose)
        
        
    
    