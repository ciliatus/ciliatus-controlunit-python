#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import uuid
import RPi.GPIO as GPIO
import ConfigParser
import controlunit
from system.log import Log
from vendors.Adafruit_DHT import Raspberry_Pi_2


class Main(object):

    controlunit = controlunit.Controlunit()
    config = ConfigParser.SafeConfigParser()

    def __heartbeat(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def run(self):
        print 'initiating'
        self.config.read('config.ini')

        GPIO.setmode(GPIO.BCM)

        while True:
            # sensorreadinggroup_id
            _uuid = uuid.uuid4()


            self.__heartbeat()
            try:
                self.controlunit.read_and_submit_sensor_data(_uuid)
            except Exception as e:
                Log('exception',
                    'Exception while Fetching and submitting sensor data: "' + str(e) + '"')

            try:
                self.controlunit.fetch_and_action_appliance_states()
            except Exception as e:
                Log('exception',
                    'Exception while Fetching and processing actions data: "' + str(e) + '"')

            print 'Sleeping ' + self.config.get('api', 'check_interval') + ' seconds'
            time.sleep(int(self.config.get('api', 'check_interval')))


def main(args):
    Main().run()
    GPIO.cleanup()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
