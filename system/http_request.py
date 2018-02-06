#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import socket
import urllib.error
import urllib.parse
import urllib.request

import system.log as log


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

    def dispatch_request(self, path, data=None, method=None, timeout=15):
        """ Sends an http request
        :param path: string with the full url
        :param data: dict with post data (optional)
        :param method: String with GET/POST/PUT/DELETE/... (optional)
        :param timeout: int for HTTP request timeout in seconds, default 15 (optional)
        :return: JSON result or None
        """
        self.logger.debug('HttpRequest.dispatch_request: Starting dispatch to %s.', path)
        socket.setdefaulttimeout(timeout)
        binary_data = None

        if data is not None:
            data = urllib.parse.urlencode(data)
            binary_data = data.encode('utf-8')

        url = self.config.get('api', 'uri') + '/' + path
        req = urllib.request.Request(url=url,
                                     data=binary_data,
                                     headers=self.headers,
                                     method=method)

        try:
            result = urllib.request.urlopen(req, timeout=timeout)
        except socket.timeout:
            self.logger.critical("HttpRequest.dispatch_request: %s timed out after %s seconds.", path, str(timeout))
            return None
        except ValueError as err:
            self.logger.critical("HttpRequest.dispatch_request: ValueError while opening url %s: %s", path, format(err))
            return None
        except urllib.error.HTTPError as err:
            self.logger.critical("HttpRequest.dispatch_request: HTTPError while opening url %s: %s\n%s",
                                 path, format(err), err.read())
            return None
        except urllib.error.URLError as err:
            self.logger.critical("HttpRequest.dispatch_request: URLError while opening url %s: %s", path, format(err))
            return None
        except Exception as err:
            self.logger.critical("HttpRequest.dispatch_request: Unknown Error while opening url %s: %s", path, format(err))
            return None

        try:
            result = result.read()
        except Exception as err:
            self.logger.critical(
                "HttpRequest.dispatch_request: Unknown Error while reading result of request to url %s: %s",
                path, format(err)
            )
            return None

        return result

    def add_header(self, name, value):
        """ Adds a header to the http request
        :param name: string
        :param value: string
        :return:
        """
        self.headers[name] = value
