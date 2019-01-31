#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
from six.moves import configparser
import io
import common

ConfigParser = configparser.ConfigParser

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)

def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined 
    Refer to the documentation for further details. 
    """     
    url = conf['global']['url']
    dl, pl = common.readcache()
    if dl == [] or pl == []:
        dl = common.retrieveDeviceList(url)
        pl = common.retrieveProgramList(url)
        common.writecache(dl, pl)
    
    spoken_name = common.simplify(str(intentMessage.slots.Device.first().value))
    spoken_word = str(intentMessage.slots.Wert.first().value).lower()

    number = -1
    if spoken_word in ['hoch', 'auf', 'an', 'herauf', 'rauf', 'up', '1', 'eins', '100%', 'angeschaltet', 'öffne', 'öffnen', 'hochfahren']:
        number = 1
    if spoken_word in ['runter', 'zu', 'aus', 'herunter', 'runter', 'down', '0', 'null', '0%', 'ausgeschaltet', 'schließe', 'schließen', 'runterfahren', 'herunterfahren']:
        number = 0

    if number > -1:
        common.changeDeviceState(url, common.getID(dl, spoken_name), number)
    
    result_sentence = "OK"
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("ndy1982:setOnOff", subscribe_intent_callback) \
         .start()


