
import collections
import cv2
import numpy as np
import json 

import argparse
import time
import sys

import datetime

from io import BytesIO 

from Dataloader import DataLoader
from Mail import Email

parser = argparse.ArgumentParser(description='Survilliance system.')
parser.add_argument('--config',  type=str, help='Configuration file path', required=True )


class Surveillance(object):

    def __init__(self, config_path, dev_type=DataLoader.DEVICE_CAM):
        """ dev_type is device type (Dataloader.py) """

        self.config_path = config_path
        self.data = None 
        self.config = None 

        self.pictures = list()
        self.email = None

        self.contour_area_restrict = 15000

        def make_config_obj():
            try:
                with open(self.config_path) as config_file:
                    self.config = json.load(config_file,
                            object_hook=lambda d: collections.namedtuple('Config', d.keys())(*d.values())) 

            except Exception as e:
                sys.stderr.write("Probably you do not have a proper json file or file is missing")
                raise(e)


        make_config_obj()
        self.data = DataLoader(dev_type, self.config.cam)
        self.deque = collections.deque(maxlen=self.config.opencv.frames.avarage) 
        self.email = Email(self.config.email)


    def run(self):

        avarage_frame = 0
        avarage_frame_init = False

        snapshot_time = datetime.datetime.now()
        reference_time = datetime.datetime.now()

        for dframe in self.data.get_data_frame():
            #cv2.imshow('Original', dframe)
            gray_scaled_frame = cv2.cvtColor(dframe, cv2.COLOR_BGR2GRAY)
    

            gaussian_blur_frame = (cv2.GaussianBlur(gray_scaled_frame,
                                    (self.config.opencv.filter.GaussianBlur.mask.row,
                                    self.config.opencv.filter.GaussianBlur.mask.column), 0))

            #cv2.imshow('Gaussian blur', gaussian_blur_frame)

            _, binary_frame = cv2.threshold(gaussian_blur_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            #cv2.imshow('Binary frame', binary_frame)

            #Initialization
            if self.deque.maxlen > len(self.deque):
                print("Waiting for another frame")
                self.deque.append(binary_frame.astype('uint16'))
                continue

            elif self.deque.maxlen == len(self.deque)  and not avarage_frame_init:
                avarage_frame = sum(self.deque)/self.deque.maxlen
                avarage_frame_init = True
                continue

            avarage_frame = sum((self.deque))/self.deque.maxlen

            without_backgroung_frame =  avarage_frame - binary_frame

            #cv2.imshow('Pict without background', without_backgroung_frame)
    
            erode_frame = cv2.erode(without_backgroung_frame.astype(np.uint8), np.ones((11, 11), np.uint8), iterations=1)
            dilate_frame = cv2.dilate(erode_frame, np.ones((15, 15), np.uint8), iterations=5)

            #cv2.imshow('Erode', erode_frame)
            #cv2.imshow('Dilate', dilate_frame)

            img, contours,hierarchy = cv2.findContours(dilate_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #cv2.imshow('Output with contours',cv2.drawContours(dframe.copy() , contours, -1, (0, 255, 0), 3))
   
            snapshot_time = datetime.datetime.now()
            

            for contour in contours:
                if cv2.contourArea(contour) < self.contour_area_restrict:
                    continue


                cnt = np.array(contour).reshape((-1,1,2)).astype(np.int32)
                cv2.drawContours(dframe, cnt, -1, (0, 255,255), 2)
                cv2.imshow("omg2", dframe)
                img_file = BytesIO(cv2.imencode('.png', dframe)[1]) 
            
                
                self.pictures.append(img_file)
                    
            if (snapshot_time - reference_time).seconds > int(self.config.email.user.timeout) and len(self.pictures):
                #send email
                self.email.send(self.pictures)

                reference_time = snapshot_time
                self.pictures = []



            self.deque.append(binary_frame.astype('uint16'))
            avarage_frame = sum(self.deque)/self.deque.maxlen
            #cv2.imshow("Avarage", avarage_frame)


if __name__ == "__main__":

    config = ""
    args = parser.parse_args()

    a = Surveillance(args.config, DataLoader.DEVICE_CAM)
    a.run()





