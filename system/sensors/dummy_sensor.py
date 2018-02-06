#!/usr/bin/env python
# -*- coding:utf-8 -*-

import configparser
import datetime
import math

import system.log as log
import system.sensors.sensor as sensor


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

    @staticmethod
    def __get_minutes_since_midnight():
        now = datetime.datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return int((now - midnight).seconds/60)

    def get_sensorreading(self):
        minutes = self.__get_minutes_since_midnight()
        temperature = 20 +  3 * (math.sin(minutes/1440*2*math.pi - 0.5*math.pi)+1)
        humidity    = 50 + 25 * (math.sin(minutes/1440*2*math.pi + 0.5*math.pi)+1)
        return {
            'humidity_percent': {
                'id': self.logical['humidity_percent'],
                'data': humidity
            },
            'temperature_celsius': {
                'id': self.logical['temperature_celsius'],
                'data': temperature
            }
        }
