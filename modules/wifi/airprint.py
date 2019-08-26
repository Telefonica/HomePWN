import os, os.path
from modules._module import Module
from utils.custom_print import print_info
from utils.airprint_generate import AirPrintGenerate
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Airptiny",
                       "Description": "This module will connect to a CUPS server and for each printer configured and marked as shared will generate a .service file for avahi that is compatible with Apple's AirPrint announcements.",
                       "Author": "Timothy J Fontaine",
                       "Module Author": "@josueencinar",
                       "Reference": "https://github.com/tjfontaine/airprint-generate/blob/master/airprint-generate.py"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost"),
                   "rport": Option.create(name="rport"),
                   "user": Option.create(name="user", description="Username to authenticate with against CUPS"),
                   "dir": Option.create(name="dir", description='Directory to create service files'),
                   "verbose": Option.create(name="verbose", value=False),
                   "prefix": Option.create(name="prefix", description='Prefix all files with this string'),
                   "admin": Option.create(name="admin", description='Include the printer specified uri as the adminurl')
                   }
        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        directory = self.args["dir"]
        if directory and not os.path.exists(directory):
                os.mkdir(directory)
    
        apg = AirPrintGenerate(
            user=self.args['user'],
            host=self.args['rhost'],
            port=self.args['rport'],
            verbose=self.args['verbose'],
            directory=directory,
            prefix=self.args['prefix'],
            adminurl=self.args['admin'],
        )
        
        apg.generate()

