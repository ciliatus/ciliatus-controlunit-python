#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import json
import urllib2

import time
from system.log import Log
from system.api_client import ApiClient
from sensors.AM2302 import SensorAM2302
import RPi.GPIO as GPIO  # import RPi.GPIO module

import pprint

class Controlunit(object):

    config = ConfigParser.SafeConfigParser()

    components = {
        'valve': {},
        'pump': {}
    }

    def __init__(self):
        self.config.read('config.ini')

        GPIO.setmode(GPIO.BCM)

        for section in self.config.sections():
            type = section.split('_')[0]
            if type == 'valve' or type == 'pump':
                self.components[type][self.config.get(section, 'id')] = {
                    'id': self.config.get(section, 'id'),
                    'state': 'stopped',
                    'pin': self.config.get(section, 'pin')
                }

        self.__init_and_reset_components()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __init_and_reset_components(self):
        for group in self.components:
            print "group: " + group
            for component_id in self.components[group]:
                    GPIO.setup(int(self.components[group][component_id]['pin']), GPIO.OUT)
                    self.__set_gpio_state(int(self.components[group][component_id]['pin']), 1)

    def __set_gpio_state(self, pin, state):
        if state == 1:
            Log('debug', 'Setting GPIO ' + str(pin) + ' to ' + str(GPIO.HIGH))
            GPIO.output(pin, GPIO.HIGH)
        elif state == 0:
            Log('debug', 'Setting GPIO ' + str(pin) + ' to ' + str(GPIO.LOW))
            GPIO.output(pin, GPIO.LOW)
        else:
            Log('error', 'Invalid GPIO state for ' + str(pin) + ': ' + str(state))

    def fetch_and_action_appliance_states(self):
        time.sleep(1)
        print 'Fetching desired states'
        with ApiClient('controlunits/' + self.config.get('main', 'id') + '/fetch_desired_states') as api:
            try:
                result = api.call()
            except urllib2.HTTPError as e:
                try:
                    result = json.loads(e.read())
                    Log('error', 'Fetching desired states failed, server returned: ' +
                        '[' + str(result["error"]["error_code"]) + '] ' + result["error"]["message"])
                except:
                    Log('error', 'Fetching desired states failed, server returned: ' + e.read())

                return

            states = result['data']

            p = pprint.PrettyPrinter(indent=4)

            for group in self.components:
                for component_id in self.components[group]:
                    if group == 'valve' and len(states['Valve']) > 0:
                        if self.components[group][component_id]['id'] in states['Valve']:
                            print 'Checking valve ' + self.components[group][component_id]['id'] + ' setting state True'
                            self.__set_gpio_state(int(self.components[group][component_id]['pin']), 1)
                        else:
                            print 'Checking valve ' + self.components[group][component_id]['id'] + ' setting state False'
                            self.__set_gpio_state(int(self.components[group][component_id]['pin']), 0)

                    if group == 'pump' and len(states['Pump']) > 0:
                        if self.components[group][component_id]['id'] in states['Pump']:
                            print 'Checking pump ' + self.components[group][component_id]['id'] + ' setting state True'
                            self.__set_gpio_state(int(self.components[group][component_id]['pin']), 1)
                        else:
                            print 'Checking pump ' + self.components[group][component_id]['id'] + ' setting state False'
                            self.__set_gpio_state(int(self.components[group][component_id]['pin']), 0)

    def read_and_submit_sensor_data(self, group_id):
        print 'Fetching and submitting sensor data'
        time.sleep(1)
        for section in self.config.sections():
            if section.split('_')[0] == 'sensor':
                write_data = False

                if not self.config.get(section, 'enabled'):
                    continue

                if self.config.get(section, 'model') == 'AM2302':
                    sensor = SensorAM2302(section)
                    data = sensor.fetch_data()
                    write_data = True

                elif self.config.get(section, 'model') == 'SR04':
                    Log('debug', 'Physical sensor data fetch failed:  "' + sensor.name + '" (' + sensor.id +
                        '). Type SR04 not yet implemented')

                else:
                    Log('debug', 'Unknown sensor type "' + self.config.get(section, 'type') + '":  "' + sensor.name +
                        '" (' + sensor.id + ')')

                if data == 'ERR':
                    Log('error', 'Physical sensor data fetching failed: "' + sensor.name + '" (' + sensor.id + ')')
                    continue

                if write_data:
                    for name, logical in data.iteritems():
                        with ApiClient('sensorreadings') as api:
                            if logical['data'] == None:
                                Log('error', 'Physical sensor "' + sensor.name + '" (' + sensor.id + ') ' +
                                    'data returned None for logical sensor ' + str(logical['id']))
                                continue

                            try:
                                result = api.call({
                                    'group_id': group_id,
                                    'logical_sensor_id': str(logical['id']),
                                    'rawvalue': str(logical['data'])
                                })
                            except urllib2.HTTPError as e:
                                result = json.loads(e.read())
                                Log('error', 'Physical sensor "' + sensor.name + '" (' + sensor.id + ') ' +
                                    'data "Logical sensor ' + str(logical['id']) + ': ' + str(logical['data']) + '" ' +
                                    'transmission failed, server returned: ' +
                                    '[' + str(result["error"]["error_code"]) + '] ' + result["error"]["message"])
                                continue

                            Log('debug', 'Physical sensor "' + sensor.name + '" (' + sensor.id + ')' +
                                'data "Logical sensor ' + str(logical['id']) + ': ' + str(logical['data']) + ' "' +
                                'transmission successful. Reading group id: "' +
                                str(group_id))
                        time.sleep(5)
        return

    # get config section by id from config.ini
    def __get_config_by_id(self, id):
        for section in self.config.sections():
            if self.config.get(section, 'id') == id:
                return section

        return False
