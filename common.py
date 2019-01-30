#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from lxml import etree
from six.moves import urllib

cache = "cache.txt"
url = conf['global']['url']

def getXML(url):
    ret = urllib.request.urlopen(url).read()
    return etree.fromstring(ret)
    #return simplexml.loads(ret)

def writecache(devicelist, programlist):
    file = open(cache, "w")
    for i in devicelist:
        file.write("Device," + i[1] + "," + i[0].encode('utf-8') + "\n")    
    for i in programlist:
        file.write("Program," + i[1] + "," + i[0].encode('utf-8') + "\n")
    file.close()

def readcache():
    devicelist = []
    programlist = []
    
    try:
        file = open(cache, "r")
        for line in file:
            print(line)
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

dl, pl = readcache()
if dl == [] or pl == []:
    dl = retrieveDeviceList(url)
    pl = retrieveProgramList(url)
    writecache(dl, pl)
