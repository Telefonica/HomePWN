from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
import shodan


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "MQTT Shodan search",
                       "Description": "With this module you will be able to check the information that Shodan has of a certain host.",
                       "Author": "@josueencinar"}

        options = {
            "apishodan": Option.create(name="apishodan", required=True),
            "rhost": Option.create(name="rhost", required=True, description="Host to check the information in Shodan")
            }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try: 
            shodan_api = shodan.Shodan(self.args["apishodan"])
            # Lookup the host
            host = shodan_api.host(self.args["rhost"])
        except Exception as e:
            print_error(e)
            print_error("Module has not been launched")
            return
        if host:
            # Print general info
            print_info(f"""
IP: {host['ip_str']}
Organization: {host.get('org', 'n/a')}
Operating System: {host.get('os', 'n/a')}
            """)

            # Print all banners
            for item in host['data']:
                    print_info(f"""
Port: {item['port']}
Banner: {item['data']}
                    """)
        else:
            print_info("No data recollected")
