import cv2
import math


class PerfDetector(object):
    sixteen = {'perfs': 2, 'height_start': 185, 'height_end': 75, 'perf_height_max': 18, 'perf_height_min': 10,
               'perf_width_max': 12, 'perf_width_min': 3}

    def __init__(self, **kwargs):
        try:
            if kwargs['gauge'] == '16mm':
                self._gauge = PerfDetector.sixteen
        except KeyError as error:
            print(error)
            raise Exception('Missing gauge argument')

    def detect_perfs(self, raw_pixels):
        perf_count = 0
        image = raw_pixels
        h, w, channels = image.shape
        image = image[h - self._gauge['height_start']:h - self._gauge['height_end'], 0:w]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]

        _, thresh = cv2.threshold(saturation, 25, 255, cv2.THRESH_BINARY)
        (_, contours, h) = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for contour in sorted_contours:
            contour_area = int(cv2.contourArea(contour))
            contour_w = int(contour_area / w)
            contour_h = int(contour_area / image.shape[0])
            print(contour_w, contour_h)
            if contour_w < self._gauge['perf_width_max'] and contour_h < self._gauge['perf_height_max']:
                if contour_w > self._gauge['perf_width_min'] and contour_h > self._gauge['perf_height_min']:
                    perf_count += 1
                    cv2.drawContours(image, contour, -1, (0, 255, 0), 3)
                    if perf_count == self._gauge['perfs']:
                        return True

        return False


if __name__ == '__main__':
    image = cv2.imread('tests/test.jpg')
    detector = PerfDetector(gauge='16mm')
    resized = cv2.resize(image, (270, 512))
    result = detector.detect_perfs(resized)

    print(result)
