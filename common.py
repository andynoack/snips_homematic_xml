#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def changeDeviceState(url, ise_id, new_value):
    if not ise_id == None:
        action_url = url + "statechange.cgi?ise_id=" + str(ise_id) + "&new_value=" + str(new_value)
        urllib.request.urlopen(action_url)

def runProgram(url, program_id):
    if not program_id == None:
        action_url = url + "runprogram.cgi?program_id=" + str(program_id)
        urllib.request.urlopen(action_url)

def getID(li, name):
    for i in li:                        
        if simplify(i[0]) in simplify(name):
            return i[1]
    return None
