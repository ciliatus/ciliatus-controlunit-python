#!/usr/bin/env python
# -*- coding:utf-8 -*-
from importlib import util
import time
import os
import system.log as log
import system.sensors.sensor as sensor
import configparser
from system.sensors.lib import Adafruit_BME280


class BME280Sensor(sensor.Sensor):

    config = configparser.ConfigParser()
    logger = log.get_logger()

    def __init__(self, config):
        try:
            util.find_spec('Adafruit_PureIO.smbus')
            import Adafruit_PureIO.smbus as smbus
        except ModuleNotFoundError:
            self.logger.critical("bme280_sensor.__init__(): Adafruit_PureIO.smbus missing")
            return
        sensor.Sensor.__init__(self)
        self.config.read('config.ini')

        self.id = self.config.get(config, 'id')
        self.name = self.config.get(config, 'name')
        self.i2c_address = self.config.get(config, 'i2c_address')

        if self.config.has_option(config, 'i2c_multiplexer_address'):
            self.i2c_multiplexer_address = self.config.get(config, 'i2c_multiplexer_address')
            self.i2c_multiplexer_port = self.config.get(config, 'i2c_multiplexer_port')
        else:
            self.i2c_multiplexer_address = None
            self.i2c_multiplexer_port = None

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
        if self.i2c_multiplexer_address and not is_second_try:
            bus = smbus.SMBus(self.config.get('i2c', 'bus'))
            bus.write_byte(int(self.i2c_multiplexer_address, 16), int(self.i2c_multiplexer_port, 16))
            self.logger.debug('BME280Sensor.__fetch_raw_data: Multiplexer on %s pointed to device %s',
                              str(self.i2c_multiplexer_address), str(self.i2c_multiplexer_port))
            time.sleep(5)
        try:
            self.logger.debug('BME280Sensor.__fetch_raw_data: Retrieving data from i2c address %s', self.i2c_address)
            s = Adafruit_BME280.BME280(address=int(self.i2c_address, 16))
            humidity = s.read_humidity()
            time.sleep(2)
            temperature = s.read_temperature()
        except Exception as err:
            if not is_second_try:
                self.logger.warning('BME280Sensor.__fetch_raw_data: Failed, retrying in 10 seconds')
                time.sleep(10)
                return self.__fetch_raw_data(True)
            else:
                self.logger.critical('BME280Sensor.__fetch_raw_data: Could not fetch data from BME280 %s: %s',
                                     str(self.name), format(err))

                i2cdetect = os.popen('i2cdetect -y ' + self.config.get('i2c', 'bus'))
                result = i2cdetect.read()
                self.logger.critical('BME280Sensor.__fetch_raw_data: Dumping i2c bus:\n%s', result)
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
