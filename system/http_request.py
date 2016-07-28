#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
from ConfigParser import SafeConfigParser


class HttpRequest(object):

    config = SafeConfigParser()
    headers = {}

    def __init__(self):
        self.config.read('config.ini')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dispatch_request(self, path, data={}):
        data = urllib.urlencode(data)
        url = self.config.get('api', 'uri') + '/' + path

        req = urllib2.Request(url, data, self.headers)
        result = urllib2.urlopen(req)

        return result.read()

    def add_header(self, name, value):
        self.headers[name] = value