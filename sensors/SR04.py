#!/usr/bin/env python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
import time
from ConfigParser import SafeConfigParser


class SensorSR04(object):

    config = SafeConfigParser()
    configname = ''
    id = 0
    pin_trigger = 0
    pin_echo = 0
    name = ''
    logical = {}

    def __init__(self, _configname):
        self.config.read('config.ini')
        self.configname = _configname
        self.id = self.config.get(self.configname, 'id')
        self.pin_trigger = self.config.get(self.configname, 'pin_trigger')
        self.pin_echo = self.config.get(self.configname, 'pin_echo')
        self.name = self.config.get(self.configname, 'name')
        logical = self.config.get(self.configname, 'logical')
        for l in logical.split('|'):
            self.logical[l.split(':')[0]] = l.split(':')[1]

        GPIO.setmode(GPIO.BCM)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def fetch_raw_data(self):
        GPIO.setup(self.pin_trigger, GPIO.OUT)
        GPIO.setup(self.pin_echo, GPIO.IN)

        GPIO.output(self.pin_trigger, False)
        time.sleep(2)
        GPIO.output(self.pin_trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.pin_trigger, False)

        pulse_start = 0
        pulse_end = 0

        while GPIO.input(self.pin_echo) == 0:
            pulse_start = time.time()

        while GPIO.input(self.pin_echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150

        GPIO.cleanup()

        return distance

    def fetch_data(self):
        raw_data = self.fetch_raw_data()
        compiled_data = {
            'distance_cm': {
                'id': self.logical['distance_cm'],
                'data': raw_data
            }
        }

        return compiled_data
