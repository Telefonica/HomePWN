from modules.shodan._shodan import ShodanModule
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from utils.shodan_search import shodan_search


class HomeModule(ShodanModule):

    def __init__(self):
        information = {"Name": "Philips Hue Shodan search",
                       "Description": "Launch this module to find philips hue lights in Shodan.",
                       "Author": "@josueencinar"}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, default_file_name="./files/shodan_philipshue.txt")

    # This function must be always implemented, it is called by the run option
    def run(self): 
        self.start('title:"hue personal"')
