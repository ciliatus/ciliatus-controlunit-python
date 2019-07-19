#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import datetime
import logging
import time
from importlib import util
from multiprocessing import Process, freeze_support
from multiprocessing.managers import BaseManager
from random import randint

import system.log as log
import system.queue as queue
from system.components import component_factory
from worker import desired_state_fetcher, sensorreading_submitter, sensorreading_buffer, maintenance

try:
    util.find_spec('RPi.GPIO')
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    log.get_logger().debug('App: Skipping RPi.GPIO module because it was not found')
    pass


class App(object):

    VERSION = 'Ciliatus Control Unit v2.0'

    logger = log.get_logger()
    config = configparser.ConfigParser()
    threads = {}
    components = None

    def __init__(self):
        self.config.read('config.ini')
        BaseManager.register('Queue', queue.Queue)
        manager = BaseManager()
        manager.start()
        self.queue = manager.Queue()
        self.threads = {
            'sensorreading_submitter': {
                'last_run': None,
                'timeout': int(self.config.get('api', 'submit_sensorreadings_interval')),
                'thread': None
            },
            'desired_state_fetcher': {
                'last_run': None,
                'timeout': int(self.config.get('api', 'fetch_desired_states_interval')),
                'thread': None
            },
            'sensorreading_buffer': {
                'last_run': None,
                'timeout': int(self.config.get('api', 'sensorreading_buffer_flush_interval')),
                'thread': None
            },
            'maintenance': {
                'last_run': None,
                'timeout': int(self.config.get('api', 'maintenance_interval')),
                'thread': None
            }
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __cleanup_components(self):
        """ Empties the ``self.components`` dict
        :return:
        """
        self.components = []

    def __load_and_setup_components(self):
        """ Loads all non-sensor components from config and sets up their gpio.
        :return:
        """
        self.logger.debug('App.__load_and_setup_components: Setting up components\' GPIO')

        self.__cleanup_components()

        try:
            util.find_spec('RPi.GPIO')
            GPIO.setmode(GPIO.BCM)
        except ModuleNotFoundError:
            self.logger.info('App.__load_and_setup_components: RPI.GPIO module not found. Did not setup GPIO mode.')
            return

        for section in self.config.sections():
            if section.split('_')[0] in ['pump', 'valve', 'generic_component']:
                if not self.__check_option_not_exists_or_is_true(section, 'enabled') \
                        or not self.config.has_option(section, 'pin'):
                    continue

                try:
                    component = component_factory.ComponentFactory.factory(section.split('_')[0], section)
                except ValueError as err:
                    self.logger.critical('DesiredStateFetcher.__load_components: %s', format(err))
                else:
                    self.components.append(component)
                    self.logger.info('App.__load_and_setup_components: Setting up %s on pin %s',
                                     self.config.get(section, 'name'), self.config.get(section, 'pin'))
                    GPIO.setup(int(self.config.get(section, 'pin')), GPIO.OUT)

                    if self.config.has_option(section, 'default_high'):
                        GPIO.output(int(self.config.get(section, 'pin')), GPIO.HIGH)

    def __check_option_not_exists_or_is_true(self, section, option):
        if self.config.has_option(section, option):
            if self.config.get(section, option) is True:
                return True
            else:
                return False
        return True

    def __spawn_thread(self, thread_name):
        """ Spawns a new thread, deletes the old one if necessary
        :param thread_name: Used to lookup the ``self.threads`` dict
                            and select the matching class and method for the thread
        :return:
        """
        self.logger.debug('App.__spawn_thread: Spawning thread %s.', thread_name)

        if not self.threads[thread_name]['thread'] is None:
            del self.threads[thread_name]['thread']

        thread_id = randint(0, 32769)
        if thread_name == 'sensorreading_submitter':
            self.threads[thread_name]['thread'] = \
                Process(
                    target=sensorreading_submitter.SensorreadingSubmitter,
                    args=(thread_id, thread_name + '-' + str(thread_id), self.queue),
                )
        elif thread_name == 'desired_state_fetcher':
            self.threads[thread_name]['thread'] = \
                Process(
                    target=desired_state_fetcher.DesiredStateFetcher,
                    args=(thread_id, thread_name + '-' + str(thread_id), self.components)
                )
        elif thread_name == 'sensorreading_buffer':
            self.threads[thread_name]['thread'] = \
                Process(
                    target=sensorreading_buffer.SensorreadingBuffer,
                    args=(thread_id, thread_name + '-' + str(thread_id), self.queue)
                )
        elif thread_name == 'maintenance':
            self.threads[thread_name]['thread'] = \
                Process(
                    target=maintenance.Maintenance,
                    args=(thread_id, thread_name + '-' + str(thread_id), self.config.get('main', 'id'), self.VERSION)
                )
        else:
            self.logger.critical('App.__spawn_thread: Unknown class name for thread: %s.', thread_name)
            return

        if __name__ == '__main__':
            freeze_support()
        self.threads[thread_name]['thread'].start()
        self.threads[thread_name]['last_run'] = datetime.datetime.now()

    def __get_last_run_seconds(self, thread_name):
        """ Returns the difference of `self.threads[thread_name]['last_run']` and now
        :param thread_name:
        :return: int Difference in seconds
        """
        return int((datetime.datetime.now() - self.threads[thread_name]['last_run']).total_seconds())

    def __check_thread_conditions_and_spawn(self, thread_name):
        """ Calls ``self.__spawn_thread`` if the thread is not running and it's configured timeout is over
        :param thread_name: Used to lookup the ``self.threads`` dict
                            and select the matching class and method for the thread
        :return:
        """
        if self.threads[thread_name]['last_run'] is None or \
                self.__get_last_run_seconds(thread_name) > self.threads[thread_name]['timeout']:
            self.__spawn_thread(thread_name)
        else:
            self.logger.debug('App.__check_thread_conditions_and_spawn: Timeout is not done yet for %s. Remaining: %ss',
                              thread_name,
                              str(self.threads[thread_name]['timeout'] - self.__get_last_run_seconds(thread_name)))

    def __check_thread(self, thread_name):
        """ Checks if a thread is alive. If not it will call ``self.__check_thread_conditions_and_spawn``
        :param thread_name: Used to lookup the ``self.threads`` dict
                            and select the matching class and method for the thread
        :return:
        """
        if self.threads[thread_name]['thread'] is None or not self.threads[thread_name]['thread'].is_alive():
            self.__check_thread_conditions_and_spawn(thread_name)
        else:
            self.logger.debug('App.__check_thread: Thread %s already running.', thread_name)

    def __check_threads(self):
        """ Checks all thread using ``self.__check_thread``
        :return:
        """
        for thread in self.threads.keys():
            self.__check_thread(thread)

    def run(self):
        """ Main loop. Watches and starts threads
        :return:
        """
        self.__load_and_setup_components()

        while True:
            self.__check_threads()
            time.sleep(2)


logger = log.setup_logger(level=logging.INFO)
config = configparser.ConfigParser()

try:
    if __name__ == '__main__':
        freeze_support()
        App().run()
except Exception as ex:
    logger.exception('Crashed, cleaning up: %s.', format(ex))
    try:
        util.find_spec('RPI.GPIO')
        GPIO.cleanup()
    except ModuleNotFoundError:
        pass
except KeyboardInterrupt:
    logger.info('Keyboard interrupt. Cleaning up and quitting.')
    try:
        util.find_spec('RPI.GPIO')
        GPIO.cleanup()
    except ModuleNotFoundError:
        pass
finally:
    logger.info('Bye')
