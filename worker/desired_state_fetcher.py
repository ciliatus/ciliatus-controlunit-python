#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import threading
import system.log as log
import configparser
import system.api_client as api_client
import system.components.component_factory as component_factory


class DesiredStateFetcher(threading.Thread):

    config = configparser.ConfigParser()
    logger = log.get_logger()
    components = []
    counter = 0

    def __init__(self, thread_id, name, components):
        self.components = components
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

        self.config.read('config.ini')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __check_option_not_exists_or_is_true(self, section, option):
        if self.config.has_option(section, option):
            if self.config.get(section, option) is True:
                return True
            else:
                return False
        return True

    def __set_component_state(self, component, state):
        """ Sets the state of a component
        :param component: A Component
        :param state: A String
        :return:
        """
        try:
            component.set_state(state)
        except Exception as err:
            self.logger.critical('DesiredStateFetcher.__set_component_state: '
                                 'Could not set component state for %s to %s: %s', component.name, state, format(err))
            return False
        else:
            return True

    def __handle_api_result(self, desired_states):
        """ Retrieves and sets all states by evaluating the desired_states dict.
        If desired_states is None it is expected that the API query resulted in an Exception.
        In that case all component will be turned off.
        :param desired_states: A dict of desired states (String)
        :return:
        """
        for component in self.components:
            if desired_states is not None:
                new_state = self.__calculate_new_component_state(desired_states, component)
                self.__set_component_state(component, new_state)
            else:
                self.__set_component_state(component, False)

    @staticmethod
    def __calculate_new_component_state(desired_states, component):
        """ If a component's desired state is contained the desired_states dict, this state will be returned
        Otherwise False will be returned to turn the component off
        :param desired_states: A dict of desired states (String)
        :param component: A Component which's new desired state should be returned
        :return:
        """
        if len(desired_states[component.type]) > 0:
            if component.id in desired_states[component.type]:
                return desired_states[component.type][component.id]
        return False

    def __retrieve_desired_states_and_set(self):
        """ Retrieves desired states for this control unit and sends them to __handle_api_result
        :return:
        """
        with api_client.ApiClient('controlunits/' + self.config.get('main', 'id') + '/fetch_desired_states') as api:
            result = api.call()
            if result is not None:
                self.__handle_api_result(result['data'])
            else:
                self.logger.critical('DesiredStateFetcher.__retrieve_desired_states_and_set: API returned None. '
                                     'See above Exception for details. All components will be turned off.')
                self.__handle_api_result(None)

    def run(self):
        """ Retrieves desired states and set component states accordingly
        :return:
        """
        started = datetime.datetime.now()
        self.logger.debug('DesiredStateFetcher.do_work: Starting')
        self.__retrieve_desired_states_and_set()
        self.logger.debug('DesiredStateFetcher.do_work: Completed after %ss',
                          int((datetime.datetime.now() - started).total_seconds()))
        return None
