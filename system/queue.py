#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import deque
from threading import Lock

from system import log


class Queue(object):

    logger = log.get_logger()
    queue = None
    lock = Lock()

    def __init__(self):
        self.queue = deque()
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def count(self):
        return len(self.queue)

    def append(self, item):
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()

    def prepend(self, item):
        self.lock.acquire()
        self.queue.appendleft(item)
        self.lock.release()

    def pop(self):
        if self.count() < 1:
            return None

        self.lock.acquire()
        item = self.queue.pop()
        self.lock.release()

        return item
