#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ConfigParser import SafeConfigParser
from vendors import Adafruit_DHT

class SensorAM2302(object):

    config = SafeConfigParser()
    configname = ''
    id = 0
    pin = 0
    name = ''
    logical = {}

    def __init__(self, _configname):
        self.config.read('config.ini')
        self.configname = _configname
        self.id = self.config.get(self.configname, 'id')
        self.pin = self.config.get(self.configname, 'pin')
        self.name = self.config.get(self.configname, 'name')
        logical = self.config.get(self.configname, 'logical')
        for l in logical.split('|'):
            self.logical[l.split(':')[0]] = l.split(':')[1]

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def fetch_raw_data(self):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, self.pin)
        return [humidity, temperature]

    def fetch_data(self):
        raw_data = self.fetch_raw_data()
        compiled_data = {
            'humidity_percent': {
                'id': self.logical['humidity_percent'],
                'data': raw_data[0]
            },
            'temperature_celsius': {
                'id': self.logical['temperature_celsius'],
                'data': raw_data[1]
            }
        }

        return compiled_data
