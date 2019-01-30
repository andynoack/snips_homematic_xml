#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
from lxml import etree
from six.moves import urllib, configparser
import io

ConfigParser = configparser.ConfigParser

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
CACHE = "cache.txt"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
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

def getXML(url):
    ret = urllib.request.urlopen(url).read()
    return etree.fromstring(ret)

def writecache(devicelist, programlist):
    file = open(CACHE, "w")
    for i in devicelist:
        file.write("Device," + str(i[1]) + "," + str(i[0].encode('utf-8')) + "\n")    
    for i in programlist:
        file.write("Program," + str(i[1]) + "," + str(i[0].encode('utf-8')) + "\n")
    file.close()

def readcache():
    devicelist = []
    programlist = []
    
    try:
        file = open(CACHE, "r")
        for line in file:
            type, id, name = line.split(",", 2)
            if type == "Device":
                devicelist.append([name.strip("\n"), int(id)])
            if type == "Program":
                programlist.append([name.strip("\n"), int(id)])            
        file.close()
    except:
        pass
    return devicelist, programlist
    
def retrieveDeviceList(url):    
    devicelist = []
    xml_devicelist = getXML(url + "devicelist.cgi")
    for device in xml_devicelist:
        save_name = ""
        save_ise_id = 0
        # Info in parent
        for pair in device.items():
            if pair[0] == 'name' and not pair[1].startswith('HM-'):
                save_name = pair[1]
        # Parse channels
        for channel in device:
            for pair in channel.items():
                if pair[0] == 'name' and not pair[1].startswith('HM-'):
                    save_name = pair[1]
                if pair[0] == 'ise_id':
                    save_ise_id = pair[1]
        if save_name != "":
            devicelist.append([save_name, save_ise_id])
    return devicelist

def retrieveProgramList(url):    
    programlist = []
    xml_programlist = getXML(url + "programlist.cgi")
    for program in xml_programlist:
        save_name = ""
        save_id = 0
        for pair in program.items():
            if pair[0] == 'name':
                save_name = pair[1]
            if pair[0] == 'id':
                save_id = pair[1]
        if save_name != "":
            programlist.append([save_name, save_id])
    return programlist

def changeDeviceState(url, ise_id, new_value):
    action_url = url + "statechange.cgi?ise_id=" + str(ise_id) + "&new_value=" + str(new_value)
    urllib.request.urlopen(action_url)

def runProgram(url, program_id):
    action_url = url + "runprogram.cgi?program_id=" + str(program_id)
    urllib.request.urlopen(action_url)

def getID(li, name):
    for i in li:
        current = i[0].lower()
        current = current.replace('ae', 'ä')
        current = current.replace('oe', 'ö')
        current = current.replace('ue', 'ü')        
        if current in name.lower():
            return i[1]
    return None

def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined 
    Refer to the documentation for further details. 
    """ 
    
    url = conf['global']['url']
    dl, pl = readcache()
    if dl == [] or pl == []:
        dl = retrieveDeviceList(url)
        pl = retrieveProgramList(url)
        writecache(dl, pl)
    
    spoken_name = intentMessage.slots.Name.first().value
    runProgram(url, getID(pl, spoken_name))
    
    result_sentence = "OK"
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("ndy1982:executeProgram", subscribe_intent_callback) \
         .start()

