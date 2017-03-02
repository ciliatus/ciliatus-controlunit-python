#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import threading
import uuid
from json import JSONDecodeError
import MyPyDHT
import system.log as log
import configparser
import urllib.error
import system.api_client as api_client
import system.sensors.sensor_factory as sensor_factory


class SensorreadingSubmitter(threading.Thread):

    config = configparser.ConfigParser()
    logger = log.get_logger()
    sensors = []
    counter = 0

    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

        self.config.read('config.ini')
        self.__load_sensors()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __cleanup_sensors(self):
        """ Empties the ``self.sensors`` dict
        :return:
        """
        self.sensors = []

    def __load_sensors(self):
        """ Loads sensors from config an creates the matching object for each sensor type.
            Then adds th em to ``self.sensors``
        :return:
        """
        self.__cleanup_sensors()
        for section in self.config.sections():
            if section.split('_')[0] == 'sensor':
                if not self.config.get(section, 'enabled'):
                    continue

                try:
                    sensor = sensor_factory.SensorFactory.factory(self.config.get(section, 'model'), section)
                except ValueError as err:
                    self.logger.warning('SensorreadingSubmitter.__load_sensors: &s', format(err))
                else:
                    self.sensors.append(sensor)

    def __handle_sensorreading(self, sensor, result, group_id):
        """
        :param sensor: A :class:`Sensor`
        :param result: A dict containing retrieved sensor readings
        :param group_id: A :class:`uuid` Reading group ids are used to calculate averages in ciliatus.
                         One run should have one randomly generated group id
        :return:
        """
        self.logger.info('SensorreadingSubmitter.__handle_sensorreading: Handling sensorreading from %s: %s',
                         sensor.name, format(result))

        if result is None:
            return

        for name, data in result.items():
            with api_client.ApiClient('sensorreadings') as api:
                try:
                    api.call({
                        'group_id': group_id,
                        'logical_sensor_id': str(data['id']),
                        'rawvalue': str(data['data'])
                    })
                except urllib.error.HTTPError as err:
                    try:
                        result = json.loads(err.read())
                    except JSONDecodeError as json_err:
                        self.logger.critical('SensorreadingSubmitter.do_work: Sensorreading push failed for '
                                             'PS %s LS %s: %s', sensor.name, str(data['id']), format(json_err))
                    else:
                        self.logger.critical('SensorreadingSubmitter.do_work: Sensorreading push failed for '
                                             'PS %s LS %s: %s', sensor.name, str(data['id']), result.error)

    def __get_sensorreading(self, sensor, group_id):
        """ Retrieves sensor reading from a single sensor
        :param sensor: A :class:`Sensor`
        :param group_id: A :class:`uuid` Reading group ids are used to calculate averages in ciliatus.
                         One run should have one randomly generated group id
        :return:
        """
        try:
            data = sensor.get_sensorreading()
        except MyPyDHT.DHTException as err:
            self.logger.critical('Could not fetch DHT sensorreading for of %s: %s', sensor.name, format(err))
        except Exception as err:
            self.logger.critical('Could not fetch sensorreading for of %s: %s', sensor.name, format(err))
        else:
            self.__handle_sensorreading(sensor, data, group_id)

    def run(self):
        """ Retrieves and sends sensorreadings from all configured sensors
        :return:
        """
        started = datetime.datetime.now()
        group_id = uuid.uuid4()

        self.logger.debug('SensorreadingSubmitter.do_work: Starting group id %s', group_id)

        for sensor in self.sensors:
            self.__get_sensorreading(sensor, group_id)

        self.logger.debug('SensorreadingSubmitter.do_work: Completed group id %s after %ss.',
                          group_id, int((datetime.datetime.now() - started).total_seconds()))

        return None
