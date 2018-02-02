#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random

import system.log as log
import system.sensors.sensor as sensor
import configparser


class DummySensor(sensor.Sensor):

    config = configparser.ConfigParser()
    logger = log.get_logger()

    def __init__(self, config):
        sensor.Sensor.__init__(self)

        self.config.read('config.ini')

        self.id = self.config.get(config, 'id')
        self.name = self.config.get(config, 'name')

        self.logical = {}
        for l in self.config.get(config, 'logical').split('|'):
            self.logical[l.split(':')[0]] = l.split(':')[1]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_sensorreading(self):
        raw_data = [random.randint(50, 99), random.randint(21, 26)]
        return {
            'humidity_percent': {
                'id': self.logical['humidity_percent'],
                'data': raw_data[0]
            },
            'temperature_celsius': {
                'id': self.logical['temperature_celsius'],
                'data': raw_data[1]
            }
        }
