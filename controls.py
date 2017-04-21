import RPi.GPIO as GPIO
from threading import Thread

import time


class Controls(object):
    def __init__(self):
        super(Controls, self).__init__()
        self.backlight_pin = 18
        self.right_stepper = {'dir': 23, 'step': 24, 'enable': 12, \
                              'vdd': 14, 'microstep': {'ms1': 22, 'ms2': 5, 'ms3': 6}}
        self.left_stepper = {'dir': 20, 'step': 21, 'enable': 16, \
                             'vdd': 16, 'microstep': {'ms1': 13, 'ms2': 19, 'ms3': 26}}
        self.mode = GPIO.setmode(GPIO.BCM)
        self.motor_stopped = False
        self.paused = False

        # dir pin high is ccw

        # set up backlight first
        GPIO.setup(self.backlight_pin, GPIO.OUT)

        for key, pin in self.right_stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.setup(value, GPIO.OUT)
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

        for key, pin in self.left_stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.setup(value, GPIO.OUT)
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

        # stop motors w/ enable pins
        GPIO.output(self.right_stepper['enable'], GPIO.HIGH)
        GPIO.output(self.left_stepper['enable'], GPIO.HIGH)

    def set_microstep_resolution(self, pins, pin_modes):
        set_microstep = lambda pin, pin_mode: GPIO.output(pin, pin_mode)
        for pin, mode in zip(pins, pin_modes):
            print(pin, mode)
            set_microstep(pin[1], mode)

    def microstep(self, resolution):
        # available resolutions - FULL, HALF, QUARTER, EIGHTH, SIXTEENTH

        if resolution is 'full':  # LOW LOW LOW
            pin_mode = [GPIO.LOW, GPIO.LOW, GPIO.LOW]
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'half':  # HIGH LOW LOW
            pin_mode = (GPIO.HIGH, GPIO.LOW, GPIO.LOW)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'quarter':  # LOW HIGH LOW
            pin_mode = (GPIO.LOW, GPIO.HIGH, GPIO.LOW)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'eighth':  # HIGH HIGH LOW
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)
        if resolution is 'sixteenth':
            pin_mode = (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
            self.set_microstep_resolution(self.right_stepper['microstep'].items(), pin_mode)
            self.set_microstep_resolution(self.left_stepper['microstep'].items(), pin_mode)

    def motor_setup(self):
        # move right stepper counter clockwise
        GPIO.output(self.left_stepper['dir'], GPIO.LOW)
        GPIO.output(self.left_stepper['enable'], GPIO.LOW)
        GPIO.output(self.right_stepper['dir'], GPIO.LOW)
        GPIO.output(self.right_stepper['enable'], GPIO.LOW)

    def motor_forward(self):
        Thread(target=self.forward, args=()).start()

    def forward(self):
        GPIO.output(self.right_stepper['step'], GPIO.HIGH)
        GPIO.output(self.right_stepper['step'], GPIO.LOW)

        if self.motor_stopped:
            self.motor_shutdown()

        if self.paused:
            self.pause()

    def feed_film(self):
        Thread(target=self.feed, args=()).start()

    def feed(self):
        GPIO.output(self.left_stepper['step'], GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(self.left_stepper['step'], GPIO.LOW)
        time.sleep(0.0001)

    def pause(self):
        GPIO.output(self.left_stepper['step'], GPIO.LOW)
        GPIO.output(self.right_stepper['step'], GPIO.LOW)

    def backlight_on(self):
        self.output = GPIO.output(self.backlightPin, GPIO.HIGH)

    def backlightOff(self):
        self.output = GPIO.output(self.backlightPin, GPIO.LOW)

    def motor_shutdown(self):
        GPIO.output(self.left_stepper['enable'], GPIO.HIGH)
        GPIO.output(self.right_stepper['enable'], GPIO.HIGH)
        for key, pin in self.right_stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

        for key, pin in self.left_stepper.items():
            if key is 'microstep':
                for microstep_pin, value in pin.items():
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

    def close(self):
        self.motor_shutdown()
        GPIO.cleanup()


if __name__ == '__main__':
    controls = Controls()
    controls.microstep('sixteenth')
    controls.motor_setup()
    controls.backlight_on()
    while True:
        for step in range(0, 100):
            time.sleep(0.004)
            controls.motor_forward()

    GPIO.output(controls.right_stepper['enable'], GPIO.HIGH)
    GPIO.output(controls.left_stepper['enable'], GPIO.HIGH)
    controls.backlight_off()
    controls.motor_stopped = True
    controls.close()
