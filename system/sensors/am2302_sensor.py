#!/usr/bin/env python
# -*- coding:utf-8 -*-
from importlib import util
import time

import system.log as log
import system.sensors.sensor as sensor
import configparser

try:
    util.find_spec('MyPyDHT')
    import MyPyDHT
except ModuleNotFoundError:
    log.get_logger().critical("am2302_sensor: MyPyDHT missing")


class AM2302Sensor(sensor.Sensor):
    config = configparser.ConfigParser()
    logger = log.get_logger()
    pin = 0

    def __init__(self, config):
        sensor.Sensor.__init__(self)
        self.config.read('config.ini')

        self.id = self.config.get(config, 'id')
        self.pin = int(self.config.get(config, 'pin'))
        self.name = self.config.get(config, 'name')
        self.logical = {}
        for l in self.config.get(config, 'logical').split('|'):
            self.logical[l.split(':')[0]] = l.split(':')[1]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __fetch_raw_data(self, is_second_try=False):
        """ Tries to fetch data from the sensor
        :param is_second_try: boolean if False a second try will be attempted on failure
        :return: dict with retrieved data or None
        """
        try:
            humidity, temperature = MyPyDHT.sensor_read(MyPyDHT.Sensor.DHT22, self.pin)
        except Exception as err:
            if not is_second_try:
                self.logger.warning('AM2302Sensor.__fetch_raw_data: Failed, retrying in 5 seconds')
                time.sleep(5)
                return self.__fetch_raw_data(True)
            else:
                self.logger.critical('AM2302Sensor.__fetch_raw_data: Could not fetch data from DHT22 on Pin %s: %s',
                                     str(self.pin), format(err))
                return None
        else:
            return [humidity, temperature]

    def get_sensorreading(self):
        """ Compiles data from ``self.__fetch_raw_data()`` to a dict
        :return:
        """
        raw_data = self.__fetch_raw_data()
        if raw_data is None:
            return None

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
