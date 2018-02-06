#!/usr/bin/env python
# -*- coding:utf-8 -*-

import configparser

import system.log as log
from system.components import component


class PumpComponent(component.Component):

    config = configparser.ConfigParser()
    logger = log.get_logger()

    def __init__(self, config):
        self.config.read('config.ini')

        self.id = self.config.get(config, 'id')
        self.pin = int(self.config.get(config, 'pin'))
        self.name = self.config.get(config, 'name')
        self.default_high = self.config.has_option(config, 'default_high')
        self.type = 'Pump'

        component.Component.__init__(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def set_state(self, new_state):
        if new_state == 'running':
            self.set_gpio_pin(True)
        else:
            self.set_gpio_pin(False)
