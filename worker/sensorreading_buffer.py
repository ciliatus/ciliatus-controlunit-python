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

    def run(self):
        self.logger.debug('SensorreadingBuffer.run(): Start flushing stash. %i items present.' % self.stash.count())
        item = self.stash.pop()
        while item is not None:
            with api_client.ApiClient('sensorreadings') as api:
                result = None
                try:
                    result = api.call({
                        'group_id': item['group_id'],
                        'logical_sensor_id': str(item['payload']['id']),
                        'rawvalue': str(item['payload']['data'])
                    })
                    self.logger.debug(
                        'SensorreadingBuffer.run(): Pushed group_id %s sensor %s' %
                        (item['group_id'], item['sensor'].name)
                    )
                except urllib.error.HTTPError as err:
                    self.stash.put(item)
                    try:
                        result = json.loads(err.read())
                    except JSONDecodeError as json_err:
                        self.logger.warning(
                            'SensorreadingBuffer.run(): Push failed, item was returned to stash for '
                            'PS %s LS %s: %s', item['sensor'].name, str(item['payload']['id']), format(json_err)
                        )
                    else:
                        self.logger.warning(
                            'SensorreadingBuffer.run(): Push failed, item was returned to stash for '
                            'PS %s LS %s: %s', item['sensor'].name, str(item['payload']['id']), result.error
                        )
                    time.sleep(5)
                if result is None:
                    self.stash.put(item)
                    self.logger.warning(
                        'SensorreadingBuffer.run(): Push failed, item was returned to stash for '
                        'PS %s LS %s', item['sensor'].name, str(item['payload']['id'])
                    )
                    time.sleep(5)

            item = self.stash.pop()

        self.logger.debug('SensorreadingBuffer.run(): Stash flush ended. %i items remaining.' % self.stash.count())
