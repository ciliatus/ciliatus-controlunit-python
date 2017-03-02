#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import base64
import json
import system.log as log
from system.http_request import HttpRequest


class ApiClient(object):

    config = configparser.ConfigParser()
    http_request = HttpRequest()
    auth_type = ''
    path = ''
    url = ''
    logger = log.get_logger()

    def __init__(self, path):
        self.config.read('config.ini')
        self.path = path

        self.auth_type = self.config.get('api', 'auth_type')
        self.__add_auth()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __add_auth(self):
        """ Leverages ``http_request.add_header`` to add authentication information
        :return:
        """
        if self.auth_type == 'basic':
            self.http_request.add_header('Authorization', 'Basic ' + base64.b64encode(
                self.config.get('api_auth_' + self.auth_type, 'user') + ':' +
                self.config.get('api_auth_' + self.auth_type, 'password')
            ))
        elif self.auth_type == 'oauth2_personal_token':
            self.http_request.add_header(
                'Authorization', 'Bearer ' + self.config.get('api_auth_' + self.auth_type, 'token')
            )

    def call(self, data=None):
        """ Executes the api call
        :param data: A dict with optional POST data
        :return: JSON data or None
        """
        raw_data = self.http_request.dispatch_request(self.path, data)

        if raw_data is None:
            return None

        try:
            json_data = json.loads(raw_data)
        except ValueError as err:
            self.logger.critical('ApiClient.call: Could not load json: %s', err)
            return None
        except Exception as err:
            self.logger.critical('ApiClient.call: Unknown exception while loading json: %s', err)
            return None

        return json_data
