import requests
from modules._module import Module
from utils.custom_print import print_info, print_error
import time
from json import dumps
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):

        information = {"Name": "Send Youtube Video",
                       "Description": "The module allows you to send a youtube video to a version 1 chromecast.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"rhost": Option.create(name="rhost", required=True),
                   "video": Option.create(name="video", required=True, 
                            description="Youtube Video ID > http://youtube.com/watch?v='video_id'")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        try:

            uri = f"http://{self.args['rhost']}:8008//apps/YouTube"
            headers = {
                'Content-Type':'application/json',
                'Origin': 'https://www.google.com',
                'Host': f"{self.args['rhost']}:8008"
            }
            data = {"v": self.args["video"]}

            response = requests.post(uri, headers=headers, data=dumps(data))
            if response.status_code == 201:
                print_info("Playing video")
            elif response.status_code == 404:
                print_error('This target no supports casting via DIAL protocol. You can use send-video-youtube-v2')
            else:
                print_error(f"Error, you should check HTTP Code: {response.status_code}")
        except Exception as e:
            print(e)