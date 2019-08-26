from access_points import get_scanner
from modules._module import Module
from utils.custom_print import print_error, print_msg
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Wifi Discover Access Points",
                       "Description": "This module allows us to see the access points using 'access_points' library. No configuration required.",
                        "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = { }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        scan = get_scanner()
        wifis = scan.get_access_points()
        print("BSSID               QUALITY    SSID")
        for w in wifis:
            self._print_access_point(w)

    def _print_access_point(self, access):
        signal = access.quality
        if signal < 30:
            color = "red"
        elif signal < 60:
            color = "yellow"
        else:
            color = "green"
        if signal <10:
            access.quality = "0"+str(access.quality)
        data = f"{access.bssid}     {access.quality}       {access.ssid}"
        print_msg(data, color=color)