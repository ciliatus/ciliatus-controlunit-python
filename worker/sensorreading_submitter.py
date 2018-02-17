#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import datetime
import traceback
import uuid
from multiprocessing import Process

import system.log as log
import system.sensors.sensor_factory as sensor_factory


class SensorreadingSubmitter(Process):

    config = configparser.ConfigParser()
    logger = log.get_logger()
    sensors = []
    counter = 0
    queue = None

    def __init__(self, thread_id, name, queue):
        Process.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.queue = queue

        self.config.read('config.ini')
        self.__load_sensors()
        self.run()

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
            Then adds them to ``self.sensors``
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
        :param sensor: :class:`Sensor`
        :param result: dict containing retrieved sensor readings
        :param group_id: :class:`uuid` Reading group ids are used to calculate averages in ciliatus.
                         One run should have one randomly generated group id
        :return:
        """
        self.logger.info('SensorreadingSubmitter.__handle_sensorreading: Handling sensorreading from %s: %s',
                         sensor.name, format(result))

        if result is None:
            return

        for name, data in result.items():
            self.queue.append({
                'payload': data,
                'group_id': group_id,
                'sensor': sensor,
                'read_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.logger.debug(
                'SensorreadingSubmitter.__handle_sensorreading: Put queue (size %i) group_id %s sensor %s',
                self.queue.count(), group_id, sensor.name
            )

    def __get_sensorreading(self, sensor, group_id):
        """ Retrieves sensor reading from a single sensor
        :param sensor: :class:`Sensor`
        :param group_id: :class:`uuid` Reading group ids are used to calculate averages in ciliatus.
                         One run should have one randomly generated group id
        :return:
        """
        try:
            data = sensor.get_sensorreading()
        except Exception as err:
            self.logger.critical('Could not fetch sensorreading of %s: %s', sensor.name, traceback.print_exc())
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
