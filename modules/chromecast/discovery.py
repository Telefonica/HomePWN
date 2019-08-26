import pychromecast
from modules._module import Module
from utils.custom_print import print_info
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "ChromeCast Discovery",
                       "Description": "Launch this module to discover chromecast within a Network.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"timeout": Option.create(name="timeout", value=5, required=True)}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        print_info("Searching devices")
        chromecasts = pychromecast.get_chromecasts(timeout=self.args["timeout"])
        if chromecasts:
            for cast in [cc for cc in chromecasts]:
                print_info(f"{cast.device.friendly_name} ({cast.device.cast_type} - {cast.device.manufacturer}) => {cast.host}")
        else:
            print_info("No devices found")