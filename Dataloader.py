
try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except:
    pass

import cv2

class DataLoader(object) :
    
    DEVICE_CAM, DEVICE_CAM_RPI = range(0, 2)

    def __init__(self, dev_type, config):

        self.dev_type = dev_type


        self.cam = None
        self.stop_cap = None
        self.cap = None

        self.__init_device()

    def __init_device(self):
        
        if self.dev_type == self.DEVICE_CAM_RPI:
            self.cam = PiCamera()
            
            try:
                self.cam.resolution = [int(config.resulution.width), int(config.resolution.height)]
            except AttributeError as e:
                print(e)
                pass

            try:
                self.cam.framerate = int(config.frame_rate)
            except AttributeError:
                print(e)
                pass

            try:
                self.cam.brightness = int(config.brightness)
            except AttributeError:
                print(e)
                pass

            try:
                self.cam.contrast = int(config.contrast)
            except AttributeError:
                print(e)
                pass

            self.cap = PiRGBArray(self.cam)
            self.stop_cap = self.cam.stop_preview

        elif self.dev_type == self.DEVICE_CAM:
            self.cap = cv2.VideoCapture(0)
            self.stop_cap = self.cap.release


        else:
            raise  ValueError("Incorrect device type had been provided.")


    def __get_files(self):
    
        if self.dev_type == self.DEVICE_CAM_RPI:
            while(True):
                frame = self.cam.capture_continuous(self.cap, format="bgr")
                yield frame

        elif self.dev_type == self.DEVICE_CAM:
            while(True):
                ret, frame = self.cap.read()
                yield frame

    def get_data_frame(self):
        try:
            for dframe in self.__get_files():
                yield dframe
    
        except StopIteration:
            self.stop_cap()

