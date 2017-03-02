#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.parse
import urllib.request
import system.log as log
import configparser


class HttpRequest(object):

    config = configparser.ConfigParser()
    headers = {}
    logger = log.get_logger()

    def __init__(self):
        self.config.read('config.ini')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dispatch_request(self, path, data=None):
        """ Sends an http request
        :param path: A string with the full url
        :param data: A dict with post data (optional)
        :return: JSON result or None
        """
        binary_data = None

        if data is not None:
            data = urllib.parse.urlencode(data)
            binary_data = data.encode('utf-8')

        url = self.config.get('api', 'uri') + '/' + path

        req = urllib.request.Request(url, binary_data, self.headers)

        try:
            result = urllib.request.urlopen(req)
        except ValueError as err:
            self.logger.critical("HttpRequest.dispatch_request: Could not open url %s: %s", path, format(err))
            return None
        except Exception as err:
            self.logger.critical("HttpRequest.dispatch_request: Unknown Exception: %s", format(err))
            return None

        return result.read()

    def add_header(self, name, value):
        """ Adds a header to the http request
        :param name: A string
        :param value: A string
        :return:
        """
        self.headers[name] = value
