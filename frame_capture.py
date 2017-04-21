from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from threading import Thread
import cv2


class FrameCapture(object):
    VALID_FORMATS = set(['tif', 'jpg', 'jpeg', 'png'])  # will add DPX and Cineon via OpenImageIO

    def __init__(self, output_dir, format, **kwargs):
        try:
            self.low_res = kwargs['low_res']
            self.hi_res = kwargs['hi_res']
        except KeyError as error:
            print(error)
            raise Exception('Missing resolution argument(s)')

        if output_dir.endswith('/'):
            self.output_dir = output_dir
        else:
            self.output_dir = "{}/".format(output_dir)

        if format in FrameCapture.VALID_FORMATS:
            self.format = format
        else:
            raise Exception('Format is not valid, must be one of {}'.format(', '.join(FrameCapture.VALID_FORMATS)))

        self.camera = PiCamera()
        self.camera.resolution = self.low_res
        self.raw = PiRGBArray(self.camera)
        self.frame_no = 0

    def init_camera(self):
        time.sleep(0.1)

    def capture_low_res(self):
        if self.camera.resolution is not self.low_res:
            self.camera.resolution = self.low_res
        self.camera.capture(self.raw, format='bgr')
        self.frame_no += 1
        return self.raw

    def capture_hi_res_async(self):
        Thread(target=self.capture_hi_res, args=()).start()

    def capture_hi_res(self):
        if self.camera.resolution is not self.hi_res:
            self.camera.resolution = self.hi_res
        self.camera.capture(self.raw, format='bgr')
        output = "{}/frame_{:06d}.{}".format(self.output_dir, self.frame_no, self.format)
        cv2.imwrite(output, self.raw)
