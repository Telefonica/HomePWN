import cv2
from json import dumps
from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option


class HomeModule(Module):

    def __init__(self):
        information = {"Name": "Video capture",
                       "Description": "With this module it's possible to capture video from an IP camera.",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"uri": Option.create(name="uri", required=True, 
                        description="URI target to capture video (example: rtsp://ip:port)")}

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        # https://stackoverflow.com/questions/49978705/access-ip-camera-in-python-opencv/51166331
        try:
            uri = int(self.args["uri"])
        except:
            uri = self.args["uri"]
        print_info("Trying to connect...")
        cam = cv2.VideoCapture(uri)
        if cam:
            while(True):
                try:
                    success, frame = cam.read()
                    if success:
                        print_ok("Connected")
                        print_info("Use q in the frame to close it")
                        # Show frame
                        cv2.imshow('frame',frame)
                        # To close
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cv2.destroyAllWindows()
                            break
                    else:
                        print_error("No connection")
                        break
                except KeyboardInterrupt:
                    break
                except:
                    pass
                    
        else:
            print_error("No connection")
