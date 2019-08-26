import pychromecast
from pychromecast.controllers.youtube import YouTubeController
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Send Youtube Video",
                       "Description": "The module allows you to send a youtube video to a version 2 chromecast.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost"),
                   "name": Option.create(name="name", description="Chromecast name"),
                   "timeout": Option.create(name="timeout"),
                   "video": Option.create(name="video", required=True, 
                            description="Youtube Video ID > http://youtube.com/watch?v='video_id'")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        if not self.args["rhost"] and not self.args["name"]:
            print_info("Show options, it's necessary to configure onename or rhost")
            return
        if str(self.args["timeout"]) == "None":
            self.args["timeout"] = 6
        try:
            chromecasts = pychromecast.get_chromecasts(timeout=self.args["timeout"])
            cast = next(cc for cc in chromecasts if (cc.device.friendly_name == self.args["name"] or cc.host == self.args["rhost"]))
            cast.wait()
            print_info("Device found, sending video")
        except:
            print_error("Device no found")
            return

        yt = YouTubeController()
        cast.register_handler(yt)
        yt.play_video(self.args["video"])
        print_ok("Done!")