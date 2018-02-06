#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Lock

from system import log


class Stash(object):

    logger = log.get_logger()
    items = []
    lock = Lock()

    def __init__(self):
        self.items = []
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def count(self):
        return len(self.items)

    def append(self, item):
        self.lock.acquire()
        self.items.append(item)
        self.lock.release()

    def prepend(self, item):
        self.lock.acquire()
        self.items.insert(0, item)
        self.lock.release()

    def pop(self):
        if len(self.items) < 1:
            return None

        self.lock.acquire()
        item = self.items.pop()
        self.lock.release()

        return item
