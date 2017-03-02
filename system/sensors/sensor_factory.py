#!/usr/bin/env python
# -*- coding:utf-8 -*-

import system.sensors.am2302_sensor as am2302_sensor


class SensorFactory(object):

    def factory(sensor_type, config):
        if sensor_type == 'AM2302':
            return am2302_sensor.AM2302Sensor(config)
        else:
            raise ValueError("Unknown sensor type: %s", sensor_type)
    factory = staticmethod(factory)
