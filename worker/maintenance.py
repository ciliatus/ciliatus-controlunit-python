#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import urllib
from json import JSONDecodeError
from multiprocessing import Process

import datetime

import system.log as log
from system import api_client


class Maintenance(Process):

    logger = log.get_logger()

    def __init__(self, thread_id, name, cu_id, version):
        Process.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.id = cu_id
        self.version = version
        self.run()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __check_in(self):
        with api_client.ApiClient('controlunits/%s/check_in' % self.id) as api:
            result = None
            try:
                client_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = api.call({
                    'software_version': self.version,
                    'client_time': client_time
                }, 'PUT')
                self.logger.debug('Maintenance.__check_in(): Pushed client time %s' % client_time)
            except urllib.error.HTTPError as err:
                self.logger.warning('Maintenance.__check_in(): Check in failed: %s' % err.reason)
                return None

            if result is None:
                self.logger.warning('Maintenance.__check_in(): Check in failed with not result')
                return None

            return True

    def run(self):
        self.logger.debug('Maintenance.run(): Checking in controlunit')
        self.__check_in()
        self.logger.debug('Maintenance.run(): Done')
