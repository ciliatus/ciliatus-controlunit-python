#!/usr/bin/env python
# -*- coding:utf-8 -*-
from system.components import generic_component
from system.components import pump_component
from system.components import valve_component


class ComponentFactory(object):

    @staticmethod
    def factory(component_type, config):
        if component_type in ['Pump', 'pump']:
            return pump_component.PumpComponent(config)
        elif component_type in ['Valve', 'valve']:
            return valve_component.ValveComponent(config)
        elif component_type in ['GenericComponent', 'generic_component']:
            return generic_component.GenericComponent(config)
        else:
            raise ValueError("Unknown component type: %s", component_type)
