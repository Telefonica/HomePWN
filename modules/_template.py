import requests
import pychromecast
from modules._module import Module
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Module Name",
                       "Description": "Module Description",
                       "Author": "@author"}

        options = {"option1": Option.create(name="option_name", value="default value", required="required?")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        print("I'm a template")
        # Implement this function to launch module
    
    # If you need auxiliary functions, you can write the ones you want