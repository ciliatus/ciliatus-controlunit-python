#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from collections import deque
from threading import Lock

from system import log


class Queue(object):

    logger = log.get_logger()
    name = 'unknown'
    queue = None
    lock = Lock()

    def __init__(self, name):
        self.queue = deque()
        self.name = name
        self.__restore()
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

    def checkpoint(self):
        self.__persist()

    def __persist(self):
        self.lock.acquire()
        try:
            with open('storage/queue-%s.json'.format(self.name), 'w') as f:
                json.dump(list(self.queue), f)
        except Exception as err:
            self.logger.critical('Queue %s could not be persisted: %s', self.name, format(err))

        self.logger.info('Queue %s persisted %s items', self.name, self.count())
        self.lock.release()

    def __restore(self):
        file = 'storage/queue-%s.json'.format(self.name)
        if not os.path.isfile(file):
            self.logger.info('Queue %s had no items to restore', self.name)
            return

        items = []
        try:
            with open(file, 'r') as f:
                items = json.loads(f)
        except Exception as err:
            self.logger.critical('Queue %s could not be restored: %s', self.name, format(err))

        for item in items:
            self.append(item)

        self.logger.info('Queue %s restored %i items', self.name, len(items))
