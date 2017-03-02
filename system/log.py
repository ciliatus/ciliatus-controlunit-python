#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name='root'):
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
    )

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = TimedRotatingFileHandler('log/controlunit.log', when='midnight')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger


def get_logger(name='root'):
    return logging.getLogger(name)
