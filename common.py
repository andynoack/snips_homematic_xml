#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lxml import etree
from six.moves import urllib
import unidecode

CACHE = "cache.txt"

def simplify(text):
    ret = unidecode.unidecode(text.lower())
    ret = ret.replace('ae', 'a')
    ret = ret.replace('oe', 'o')
    ret = ret.replace('ue', 'u')
    return ret

def getXML(url):
    ret = urllib.request.urlopen(url).read()
    return etree.fromstring(ret)

def writecache(devicelist, programlist):
    file = open(CACHE, "w")
    for i in devicelist:
        file.write("Device," + str(i[1]) + "," + str(i[0]) + "\n")    
    for i in programlist:
        file.write("Program," + str(i[1]) + "," + str(i[0]) + "\n")
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
                save_name = simplify(pair[1])
        # Parse channels
        for channel in device:
            for pair in channel.items():
                if pair[0] == 'name' and not pair[1].startswith('HM-'):
                    save_name = simplify(pair[1])
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
                save_name = simplify(pair[1])                
            if pair[0] == 'id':
                save_id = pair[1]
        if save_name != "":
            programlist.append([save_name, save_id])
    return programlist

def getState(url, name):    
    programlist = []
    action_url = url + "statelist.cgi?show_internal=0"
    print(action_url)
    xml_statelist = getXML(action_url)
    simplename = simplify(name)
    
    found = 0
    devicetype = False
    value = None
    
    for device in xml_statelist:
        for pair in device.items():
            if pair[0] == 'name' and not pair[1].startswith('HM-'):
                if simplify(pair[1]) == simplename:
                    found = 1
        for channel in device:
            for pair in channel.items():
                if pair[0] == 'name' and not pair[1].startswith('HM-'):
                    if simplify(pair[1]) == simplename:
                        found = 1
                if found == 1:
                    for datapoint in channel:
                        if found == 1:
                            for pair in datapoint.items():
                                if pair[0] == 'name' and 'MOTION' in pair[1]:
                                    devicetype = 'motion'
                                if pair[0] == 'name' and 'LEVEL' in pair[1]:
                                    devicetype = 'level'
                                if pair[0] == 'name' and 'STATE' in pair[1]:
                                    devicetype = 'state'
                                if pair[0] == 'value' and devicetype:
                                    value = pair[1]
                                    found = 2
                                    break
    if found == 2:
        if devicetype == 'motion':
            if value == 'true':
                return 'Bewegung erkannt!'
            else:
                return 'keine Bewegung erkannt.'                
        if devicetype == 'state':
            if value == 'true':
                return 'an'
            else:
                return 'aus'
        if devicetype == 'level':
            return str(int(float(value)*100))+'%'
    return False  

def changeDeviceState(url, ise_id, new_value):
    if not ise_id == None:
        action_url = url + "statechange.cgi?ise_id=" + str(ise_id) + "&new_value=" + str(new_value)
        urllib.request.urlopen(action_url)
        return True
    return False

def runProgram(url, program_id):
    if not program_id == None:
        action_url = url + "runprogram.cgi?program_id=" + str(program_id)
        urllib.request.urlopen(action_url)
        return True
    return False

def getID(li, name):
    for i in li:                        
        if simplify(i[0]) in simplify(name):
            return i[1]
    return None
