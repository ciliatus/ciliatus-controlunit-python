#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
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

    i2c_address = 0
    i2c_multiplexer_address = 0
    i2c_multiplexer_port = 0

    def __init__(self):
        sensor.Sensor.__init__(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def point_multiplexer(self):
        """
        Points an I2C multiplexer to the desired channel.
        Tested with TCA9548A
        """
        bus = smbus.SMBus(self.config.get('i2c', 'bus'))

        bin_channel = int(math.pow(2, self.i2c_multiplexer_port))

        bus.write_byte(self.i2c_multiplexer_address, bin_channel)

        self.logger.debug('I2CSensor.__point_multiplexer: Multiplexer on %s pointed to channel %i',
                          str(self.i2c_multiplexer_address), self.i2c_multiplexer_port)

        time.sleep(0.1)

        self.logger.debug('I2CSensor.__point_multiplexer: Multiplexer reports channel %s',
                          str(bus.read_byte(self.i2c_multiplexer_address)))
        time.sleep(0.1)
