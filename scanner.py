from controls import Controls
from frame_capture import FrameCapture
from perf_detector import PerfDetector
import time

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scan some film")
    parser.add_argument('-f', '--format', help="the output format. (jpg, tif, png)", required="true",
                        type=str)
    parser.add_argument('-o', '--output', help="Path of Output Directory.", required="true")

    args = vars(parser.parse_args())

    format = args['format']
    output = args['output']

    controls = Controls()
    controls.microstep('sixteenth')
    controls.motor_setup()
    controls.backlight_on()
    capture = FrameCapture(output, format, low_res=(270, 512), hi_res=(1080, 2048))
    detector = PerfDetector(gauge='16mm')
    while True:
        for step in range(0, 50):
            time.sleep(0.004)
            controls.motor_forward()
            frame = capture.capture_low_res()
            if detector.detect_perfs(frame) is True:
                capture.capture_hi_res_async()
