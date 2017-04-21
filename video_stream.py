from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread


class VideoStream(object):
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)
        self.preview_window = (0, 0, 640, 480)
        self.camera.framerate = 15
        self.stream = None
        self.rgb_array = PiRGBArray(self.camera, size=self.camera.resolution)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped

        self.frame = None
        self.preview_stopped = False
        self.capture_stopped = False

    def capture_hi_res(self):
        self.stream = self.camera.capture_continuous(self.rgb_array, use_video_port=True, splitter_port=2, format='bgr')
        Thread(target=self.capture_raw, args=()).start()

    def capture_raw(self):

        for f in self.stream:
            self.frame = f.array
            self.rgb_array.truncate(0)

            if self.capture_stopped:
                self.stream.close()
                self.rgb_array.close()
                self.camera.close()


    def stop_capture(self):
        self.capture_stopped = True

    def preview_stream(self):

        # start the thread to read frames from the video stream
        Thread(target=self.preview, args=()).start()

    def preview(self):
        self.camera.start_preview(fullscreen=False, window=self.preview_window)

        if self.preview_stopped:
            self.camera.stop_preview()

    def read(self):
        return self.frame

    def stop_preview(self):
        self.preview_stopped = True
