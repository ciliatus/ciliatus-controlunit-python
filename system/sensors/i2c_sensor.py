#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
from importlib import util

import system.log as log
import system.sensors.sensor as sensor

try:
    util.find_spec('Adafruit_PureIO.smbus')
    import Adafruit_PureIO.smbus as smbus
except ModuleNotFoundError:
    log.get_logger().critical("i2c_sensor: Adafruit_PureIO.smbus missing")


class I2CSensor(sensor.Sensor):

    logger = log.get_logger()

    i2c_address = ''
    i2c_multiplexer_address = ''
    i2c_multiplexer_port = ''
    i2c_channels = {
        0: 0b00000001,
        1: 0b00000010,
        2: 0b00000100,
        3: 0b00001000,
        4: 0b00010000,
        5: 0b00100000,
        6: 0b01000000,
        7: 0b10000000
    }

    def __init__(self):
        sensor.Sensor.__init__(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def point_multiplexer(self):
        bus = smbus.SMBus(self.config.get('i2c', 'bus'))
        bus.write_byte(int(self.i2c_multiplexer_address, 16), self.i2c_channels[self.i2c_multiplexer_port])
        self.logger.debug('I2CSensor.__point_multiplexer: Multiplexer on %s pointed to channel %s',
                          str(self.i2c_multiplexer_address), str(self.i2c_multiplexer_port))
        time.sleep(0.1)
        self.logger.debug('I2CSensor.__point_multiplexer: Multiplexer reports channel %s',
                          str(bus.read_byte(int(self.i2c_multiplexer_address, 16))))
        time.sleep(0.1)
