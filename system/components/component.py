#!/usr/bin/env python
# -*- coding:utf-8 -*-
import importlib
from importlib import util

import system.log as log
import configparser

try:
    importlib.util.find_spec('RPi.GPIO')
    import RPi.GPIO
except ModuleNotFoundError:
    pass


class Component(object):

    config = configparser.ConfigParser()
    logger = log.get_logger()
    pin = 0
    name = ''

    def __init__(self):
        self.config.read('config.ini')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_gpio_pin(self, new_state: bool):
        self.logger.debug('Component.set_gpio_pin: Setting pin %s of component %s to %s.',
                         str(self.pin), self.name, str(new_state))

        GPIO.output(self.pin, new_state)
