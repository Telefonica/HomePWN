# Adapting script from 
# Thanks to 
# Author: @lucferbux

from modules._module import Module
from utils.custom_print import print_error
from utils.qr_reader import display_qr
from utildata.dataset_options import Option
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import time

class HomeModule(Module):

    def __init__(self):
        information = {"Name": "QR Reader Webcam",
                       "Description": "This module allows you to read QR codes through the Webcam. It gives you the option to save this code in a file.",
                       "OS": "Linux",
                       "Author": "@lucferbux"}

        options = {
            'file': Option.create(name="file", value="qr_webcam.png", required=True, description="destination file"),
            'save_capture': Option.create(name="save_capture", value=False, description="if the image captured of the qr is stored"),
            'verbose': Option.create(name="verbose", value=False, description="verbose mode"),
        }

        # Constructor of the parent class
        super(HomeModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    def run(self):
        verbose = str(self.args.get("verbose", "False")).lower() == "true"
        save_capture = str(self.args.get("save_capture", "False")).lower() == "true"
        path = self.args.get("file", "qr_webcam.png")
        if("/" not in path):
            path = f"./files/{path}"
        
        
        self.capture_qr(verbose, path, save_capture)
                 
    def capture_qr(self, verbose, path, save_capture):
        """Get the webcam and wait for a qr image
        
        Args:
            verbose (Boolean): Verbose mode
            path (str): Path to store the image
            save_capture (Boolean): Set to true to save the image
        """
        cap = cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)
        time.sleep(1)
    
        while(cap.isOpened()):
            ret, frame = cap.read()
            im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            read = decode(im)        
            cv2.imshow('frame',frame)
            if(read):
                display_qr(read, verbose)
                if(save_capture):
                    cv2.imwrite(path, frame)   
                cap.release()
                cv2.destroyAllWindows()
                break
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
                  

        
    
                

                
