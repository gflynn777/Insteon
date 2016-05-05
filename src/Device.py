import re, binascii
from time import sleep
from Command import Command
from Util import Util, SerialInstance

class Device:
    PLM = bytes([0x31, 0x18, 0xCF])
    MAIN_LAMP = bytes([0x18, 0x97, 0x52])
    NEW_RLINC = bytes([0x3E, 0xD0, 0x8B])
    BED_RLINC = bytes([0x1C, 0x4E, 0x32])
    BED_LAMP = bytes([0x26, 0x5A, 0x46])
    FIRST_ALDB_ADDRESS = 0xFF
    DEV_DATA_1 = 21
    DEV_DATA_2 = 22
    DEV_DATA_3 = 23
    DEV_END = 24
    
    def __init__(self, name):
        self.name = name.upper()
        self.deviceId = binascii.unhexlify(name)
        self.aldb = []
        self.freeAldb = self.traverseAldb(Device.FIRST_ALDB_ADDRESS)
        self.setDataBytes()
        self.links = []
        
    def setDataBytes(self):
        self.data1 = self.getMostCommonHex(Device.DEV_DATA_1)
        self.data2 = self.getMostCommonHex(Device.DEV_DATA_2)
        self.data3 = self.getMostCommonHex(Device.DEV_DATA_3)
        self.data4 = self.getMostCommonHex(Device.DEV_END)
        
    def addToAldb(self, string):
        if string not in self.aldb:
            self.aldb.append(string)
        
    def printAldb(self):
        print('Device: %s' % self.name)
        for x in range(len(self.aldb)):
            print('%d: %s' % (x, Command.spaceOut(Command.bToS(self.aldb[x]))))
        
    def traverseAldb(self, startAddress):
        
        while startAddress > 0x00:
            print("Checking: 0x%0.2x" % startAddress)
            SerialInstance().ser.flushInput()
            SerialInstance().ser.flushOutput()
            Command.queryMemory(self.deviceId, bytes([0x0F, startAddress]))
            i = SerialInstance().ser.readline()
            sleep(.3)
            #Keep reading the address until we don't get a NACK
            if re.search(r'(\w)+(15)\b', Command.bToS(i)):
                print('Received NACK')
                continue #This makes it stop here and try again
                
            elif re.search(r'(\w)+(06)\b', Command.bToS(i)):
                for _ in range(50):
                    SerialInstance().ser.flushInput()
                    SerialInstance().ser.flushOutput()
                    i = SerialInstance().ser.readline()
                    cmdStr = Command.bToS(i)
                    if len(i) > 0:
                        print("06: %s" % cmdStr)
                    if (len(i) > 0 and len(cmdStr) == 50):
                        self.addToAldb(i)
                        startAddress = startAddress - 0x08
                        print("address Decremented")
                        break
            if re.search(r'(\w)+0(0|1)0000000000000000(\w\w){0,1}\b', Command.bToS(i)):
                print("Found blank address: %02x" % startAddress)
                return bytearray([i[13], i[14]])
            
    def refreshAldb(self):
        self.aldb = []
        self.freeAldb = self.traverseAldb(Device.FIRST_ALDB_ADDRESS)
        self.setDataBytes()
    
    def confirmFreeMem(self):
        nextFree = self.traverseAldb(self.freeAldb[1])
        if self.freeAldb == nextFree:
            print("saved address was correct")
        return nextFree
    
    def getMostCommonHex(self, position):
        #Position should be either 22, 23, 24
        equalsGroupNum = [] #Dev_Data_3 sometimes equals the group number.
        elements = []
        for _, address in enumerate(self.aldb):
            elements.append(address[position])
            equalsGroupNum.append(address[position] == address[17] and position == Device.DEV_DATA_3)
            if position == Device.DEV_END and address[position] != 0x00:
                return 0xbad
            
        #The below method returns true if true is the most common value
        if Util.most_common(equalsGroupNum):
            return 0xbad
        return Util.most_common(elements)
                
    def addLinkToAldb(self, deviceTolink, groupNum):
        msg = bytearray([0x02, 0x62])
        msg.extend(self.deviceId)
        msg.extend([0x1F, 0x2f, 0x00, 0x00, 0x00, 0x02])
        msg.extend(self.confirmFreeMem())
        msg.append(0x08)
        if True: #self.isController:
            msg.append(0xE2)
        else:
            msg.append(0xA2)
        msg.append(groupNum)
        msg.extend(deviceTolink.deviceId)
        #Device Data - based on other aldb data
        msg.append(self.data1)
        msg.append(self.data2)
        if self.data3 == 0xbad: #Code used for same as groupNum
            msg.append(groupNum)
        else:
            msg.append(self.data3)
        if self.data4 == 0xbad: #Must be a checksum
            msg.append(Util.getChecksum(msg))
        else:
            msg.append(self.data4)
        print('ALDB Add: %s' % Command.spaceOut(Command.bToS(msg)))
        
    def addDeviceLink(self):
        self.links.append
        
class Link:
    CONTROLLER = 0
    RESPONDER = 1
    
    def __init__(self, fromDev, toDev, devType, group):
        self.fromDev = fromDev
        self.toDev = toDev
        self.group = group
        self.devType = devType
        if devType == Link.CONTROLLER:
            self.name = fromDev.name +" is controller for "+ Command.bToS(toDev)
        else:
            self.name = fromDev.name +" is a responder to "+ Command.bToS(toDev) +" Group: "+ group
            
class Scene:
    
    def __init__(self, name):
        self.name = name
        self.responders = []
        self.controllers = []
        self.controllerGroupLookup = {}
        
    def addResponder(self, device):
        self.responders.append(device)
        for ctrlDevice in self.controllers:
            device.addLinkToAldb(ctrlDevice, self.controllerGroupLookup[ctrlDevice])
            ctrlDevice.addLinkToAldb(device, self.controllerGroupLookup[ctrlDevice])
        
    def addController(self, device, groupNum):
        self.controllers.append(device)
        self.controllerGroupLookup[device] = groupNum
        for respDevice in self.responders:
            device.addLinkToAldb(respDevice, groupNum)
            respDevice.addLinkToAldb(device, groupNum)
        
        
        
        