from modules.shodan._shodan import ShodanModule
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from utils.shodan_search import shodan_search
from utils.shell_options import ShellOptions


class HomeModule(ShodanModule):

    def __init__(self):
        information = {"Name": "IP Camera Shodan search",
                       "Description": """Launch this module with your Shodan API Key to get IP addresses for cams. Possible searches:
    - Abelcam: abelcam
    - Netwave: Server: Netwave IP Camera
    - Webcamxp: webcamxp
    - Vivotek: Vivotek Network Camera
    - Blue Iris: http.favicon.hash:-520888198
    - Netatmo: lighttpd 1.4.35 404 port:"80" 345""",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {
            "search": Option.create(name="file", value="Server: Netwave IP Camera 200 OK", required=True, description="Camera to search")
            }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options, "./files/shodan_camera.txt")

    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        s_options.add_set_option_values("search", ["abelcam", "Server: Netwave IP Camera", "webcamxp", "Vivotek Network Camera", 
                                                    "http.favicon.hash:-520888198", "lighttpd 1.4.35 404 port:'80' 345"])
    
    # This function must be always implemented, it is called by the run option
    def run(self): 
        self.start(self.args["search"] + " 200 OK")