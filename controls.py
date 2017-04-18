import RPi.GPIO as GPIO
from threading import Thread

import time


class Controls(object):
    def __init__(self):
        super(Controls, self).__init__()
        self.backlightPin = 18
        self.rightStepper = {'dir': 23, 'step': 24, 'enable': 12, \
                             'vdd': 14, 'microstep': {'ms1': 22, 'ms2': 5, 'ms3': 6}}
        self.leftStepper = {'dir': 20, 'step': 21, 'enable': 16, \
                            'vdd': 16, 'microstep': {'ms1': 13, 'ms2': 19, 'ms3': 26}}
        self.mode = GPIO.setmode(GPIO.BCM)
        self.motorStopped = False
        self.paused = False

        # dir pin high is ccw

        # set up backlight first
        GPIO.setup(self.backlightPin, GPIO.OUT)

        for key, pin in self.rightStepper.items():
            if key is 'microstep':
                for microstepPin, value in pin.items():
                    GPIO.setup(value, GPIO.OUT)
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

        for key, pin in self.leftStepper.items():
            if key is 'microstep':
                for microstepPin, value in pin.items():
                    GPIO.setup(value, GPIO.OUT)
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

        # stop motors w/ enable pins
        GPIO.output(self.rightStepper['enable'], GPIO.HIGH)
        GPIO.output(self.leftStepper['enable'], GPIO.HIGH)

    def setMicrostepResolution(self, pins, pinModes):
        setMicrostep = lambda pin, pinMode: GPIO.output(pin, pinMode)
        for pin, mode in zip(pins, pinModes):
            print(pin, mode)
            setMicrostep(pin[1], mode)

    def microstep(self, resolution):
        # available resolutions - FULL, HALF, QUARTER, EIGHTH, SIXTEENTH

        if resolution is 'full':  # LOW LOW LOW
            pinMode = [GPIO.LOW, GPIO.LOW, GPIO.LOW]
            self.setMicrostepResolution(self.rightStepper['microstep'].items(), pinMode)
            self.setMicrostepResolution(self.leftStepper['microstep'].items(), pinMode)
        if resolution is 'half':  # HIGH LOW LOW
            pinMode = (GPIO.HIGH, GPIO.LOW, GPIO.LOW)
            self.setMicrostepResolution(self.rightStepper['microstep'].items(), pinMode)
            self.setMicrostepResolution(self.leftStepper['microstep'].items(), pinMode)
        if resolution is 'quarter':  # LOW HIGH LOW
            pinMode = (GPIO.LOW, GPIO.HIGH, GPIO.LOW)
            self.setMicrostepResolution(self.rightStepper['microstep'].items(), pinMode)
            self.setMicrostepResolution(self.leftStepper['microstep'].items(), pinMode)
        if resolution is 'eighth':  # HIGH HIGH LOW
            pinMode = (GPIO.HIGH, GPIO.HIGH, GPIO.LOW)
            self.setMicrostepResolution(self.rightStepper['microstep'].items(), pinMode)
            self.setMicrostepResolution(self.leftStepper['microstep'].items(), pinMode)
        if resolution is 'sixteenth':
            pinMode = (GPIO.HIGH, GPIO.HIGH, GPIO.HIGH)
            self.setMicrostepResolution(self.rightStepper['microstep'].items(), pinMode)
            self.setMicrostepResolution(self.leftStepper['microstep'].items(), pinMode)

    def motorSetup(self):
        # move right stepper counter clockwise
        GPIO.output(self.leftStepper['dir'], GPIO.LOW)
        GPIO.output(self.leftStepper['enable'], GPIO.LOW)
        GPIO.output(self.rightStepper['dir'], GPIO.LOW)
        GPIO.output(self.rightStepper['enable'], GPIO.LOW)

    def motorForward(self):
        Thread(target=self.forward, args=()).start()

    def forward(self):

        for i in range(10):
            GPIO.output(self.leftStepper['step'], GPIO.HIGH)
            time.sleep(0.0001)
            GPIO.output(self.leftStepper['step'], GPIO.LOW)
            time.sleep(0.0001)
            GPIO.output(self.rightStepper['step'], GPIO.HIGH)
            time.sleep(0.0001)
            GPIO.output(self.rightStepper['step'], GPIO.LOW)
            time.sleep(0.0001)

        if self.motorStopped:
            self.motorShutdown()

        if self.paused:
            self.pause()

    def pause(self):
        GPIO.output(self.leftStepper['step'], GPIO.LOW)
        GPIO.output(self.rightStepper['step'], GPIO.LOW)

    def backlightOn(self):
        self.output = GPIO.output(self.backlightPin, GPIO.HIGH)

    def backlightOff(self):
        self.output = GPIO.output(self.backlightPin, GPIO.LOW)

    def motorShutdown(self):
        GPIO.output(self.leftStepper['enable'], GPIO.HIGH)
        GPIO.output(self.rightStepper['enable'], GPIO.HIGH)
        for key, pin in self.rightStepper.items():
            if key is 'microstep':
                for microstepPin, value in pin.items():
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

        for key, pin in self.leftStepper.items():
            if key is 'microstep':
                for microstepPin, value in pin.items():
                    GPIO.output(value, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.LOW)

    def close(self):
        self.motorShutdown()
        GPIO.cleanup()

if __name__ == '__main__':
    controls = Controls()
    controls.microstep('sixteenth')
    controls.motorSetup()

    for step in range(0, 1000):
        time.sleep(0.005)
        controls.motorForward()

    GPIO.output(controls.rightStepper['enable'], GPIO.HIGH)
    GPIO.output(controls.leftStepper['enable'], GPIO.HIGH)
    controls.motorStopped = True
    controls.close()

