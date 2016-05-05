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
        self.name = name
        self.deviceId = binascii.unhexlify(name)
        self.aldb = []
        self.freeAldb = self.traverseAldb(Device.FIRST_ALDB_ADDRESS)
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
    
    @staticmethod
    def putDevice(msg, address):
        msg.append(address[0])
        msg.append(address[1])
        msg.append(address[2])
        
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
                for x in range(50):
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
                print("Found blank address: 0x0F%s" % startAddress)
                return bytearray([i[13], i[14]])
    
    def confirmFreeMem(self):
        nextFree = self.traverseAldb(self.freeAldb[1])
        if self.freeAldb == nextFree:
            print("saved address was correct")
        return nextFree
    
    def getMostCommonHex(self, position):
        #Position should be either 22, 23, 24
        equalsGroupNum = [] #Dev_Data_3 sometimes equals the group number.
        elements = []
        for idx, address in enumerate(self.aldb):
            elements.append(address[position])
            equalsGroupNum.append(address[position] == address[17] and position == Device.DEV_DATA_3)
            
        #The below method returns true if true is the most common
        if Util.most_common(equalsGroupNum):
            return 0xbad
        return Util.most_common(elements)
        
    
