#!/usr/bin/env python
# -*- coding:utf-8 -*-

import system.sensors.am2302_sensor as am2302_sensor
import system.sensors.bme280_sensor as bme280_sensor


class SensorFactory(object):

    def factory(sensor_type, config):
        if sensor_type == 'AM2302':
            return am2302_sensor.AM2302Sensor(config)
        if sensor_type == 'BME280':
            return bme280_sensor.BME280Sensor(config)
        else:
            raise ValueError("Unknown sensor type: %s", sensor_type)
    factory = staticmethod(factory)
