from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2


class VideoStream(object):
    def __init__(self):
        super(VideoStream, self).__init__()
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)
        self.previewWindow = (0, 0, 640, 480)
        self.camera.framerate = 15
        self.stream = None
        self.rgbArray = PiRGBArray(self.camera, size=self.camera.resolution)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped

        self.frame = None
        self.previewStopped = False
        self.captureStopped = False

    def captureHiRes(self):
        self.stream = self.camera.capture_continuous(self.rgbArray, use_video_port=True, splitter_port=2, format='bgr')
        Thread(target=self.captureRaw, args=()).start()
        return self

    def captureRaw(self):

        for f in self.stream:
            self.frame = f.array
            self.rgbArray.truncate(0)

            if self.captureStopped:
                self.stream.close()
                self.rgbArray.close()
                self.camera.close()
                return

    def stopCapture(self):
        self.captureStopped = True

    def previewStream(self):

        # start the thread to read frames from the video stream

        Thread(target=self.preview, args=()).start()
        return self

    def preview(self):
        self.camera.start_preview(fullscreen=False, window=self.previewWindow)

        if self.previewStopped:
            self.camera.stop_preview()

    def read(self):
        return self.frame

    def stopPreview(self):
        self.previewStopped = True
