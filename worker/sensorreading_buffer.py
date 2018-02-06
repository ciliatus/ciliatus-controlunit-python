#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import urllib
from json import JSONDecodeError
from multiprocessing import Process

import system.log as log
from system import api_client


class SensorreadingBuffer(Process):

    logger = log.get_logger()
    stash = None

    def __init__(self, thread_id, name, stash):
        Process.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.stash = stash
        self.run()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __submit_sensorreading(self, item):
        with api_client.ApiClient('sensorreadings') as api:
            result = None
            try:
                result = api.call({
                    'group_id': item['group_id'],
                    'logical_sensor_id': str(item['payload']['id']),
                    'rawvalue': str(item['payload']['data']),
                    'read_at': item['read_at']
                })
                self.logger.debug(
                    'SensorreadingBuffer.run(): Pushed group_id %s sensor %s' %
                    (item['group_id'], item['sensor'].name)
                )
            except urllib.error.HTTPError as err:
                if err.code == 422:
                    self.logger.critical(
                        'SensorreadingBuffer.run(): Push failed. Sensorreading not processable. Discarding PS %s LS %s',
                        item['sensor'].name, str(item['payload']['id'])
                    )
                    return None

                self.stash.prepend(item)
                self.logger.warning(
                    'SensorreadingBuffer.run(): Push failed with error. Item was returned to stash (size: %i) for '
                    'PS %s LS %s: %s',
                    self.stash.count(), item['sensor'].name, str(item['payload']['id']), err.reason
                )
                return None

            if result is None:
                self.stash.prepend(item)
                self.logger.warning(
                    'SensorreadingBuffer.run(): Push failed with not error. Item was returned to stash (size: %i) for '
                    'PS %s LS %s',
                    self.stash.count(), item['sensor'].name, str(item['payload']['id'])
                )
                return None

            return True

    def run(self):
        self.logger.debug('SensorreadingBuffer.run(): Start flushing stash. %i items present.' % self.stash.count())
        item = self.stash.pop()
        while item is not None:
            result = self.__submit_sensorreading(item)

            if result is None:
                time.sleep(5)

            item = self.stash.pop()

        self.logger.debug('SensorreadingBuffer.run(): Stash flush ended. %i items remaining.' % self.stash.count())
