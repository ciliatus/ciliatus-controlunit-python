#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import base64
import json
from system.log import Log
from system.http_request import HttpRequest

class ApiClient(object):

    config = ConfigParser.SafeConfigParser()
    http_request = HttpRequest()
    auth_type = ''
    path = ''
    url = ''

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
        if self.auth_type == 'basic':
            self.http_request.add_header('Authorization', 'Basic ' + base64.b64encode(
                self.config.get('api_auth_' + self.auth_type, 'user') + ':' +
                self.config.get('api_auth_' + self.auth_type, 'password')
            ))

    def call(self, data=None):
        rawdata = self.http_request.dispatch_request(self.path, data)
        try:
            jsonData = json.loads(rawdata)
        except Exception:
            Log('error', 'Exception while parsing API result from request ' + self.path + ' with ' + data + ''
                         '. Rawdata: ' + rawdata)
            return

        return jsonData
