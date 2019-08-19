import requests
import pychromecast
from modules._module import Module
from utils.custom_print import print_info, print_error



class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Module Name",
                       "Description": "Module Description",
                       "Author": "@author"}

        # -----------name-----default_value--description--required?
        options = {"option1": [None, "Option description", True]}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    def run(self):
        print("I'm a template")
        # Implement this function to launch module
    
    # If you need auxiliary functions, you can write the ones you want