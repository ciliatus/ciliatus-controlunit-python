#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import json
import urllib2

from system.log import Log
from system.api_client import ApiClient
from sensors.AM2302 import SensorAM2302


class Controlunit(object):

    config = ConfigParser.SafeConfigParser()

    def __init__(self):
        self.config.read('config.ini')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read_and_submit_sensor_data(self, group_id):
        print 'Fetching and submitting sensor data'
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
        return

    def fetch_and_process_pending_actions(self):
        pass

    # get config section by id from config.ini
    def __get_config_by_id(self, id):
        for section in self.config.sections():
            if self.config.get(section, 'id') == id:
                return section

        return False
