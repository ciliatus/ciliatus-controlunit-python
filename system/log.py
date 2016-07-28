#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime


class Log:

    def __init__(self, level, text):
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

        prefix = ''
        if level == 'error':
            prefix = FAIL
        elif level == 'warning':
            prefix = WARNING
        elif level == 'success':
            prefix = OKGREEN
        elif level == 'debug':
            prefix = OKBLUE
        elif level == 'exception':
            prefix = BOLD + FAIL

        print prefix + '[' + level + ']: ' + text + ENDC

        with open("tc.log", "a") as f:
            f.write(str(datetime.now()) + prefix + '[' + level + ']: ' + text + '\n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
