"""
0x02 - Start of IM cmd
0x06 - ACK
0x15 - NACK (negative acknowledgment)
0x50 - Standard message received (after 0x02)
0x60 - Get IM info
0x6D - LED On
0x6E - LED OFF
0x69 - Get first All-link record
0x62 - Get Next All-link record
"""
import binascii
from Util import SerialInstance

class Command:
    """Holds a single Insteon Command""" #Ref'd by Command.__doc__
    GET_IM_INFO = 0x60
    FAST_ON = 0x12
    FAST_OFF = 0x14
    STATUS = 0x19
    GET_FIRST_ALL_LINK = 0X69
    GET_NEXT_ALL_LINK = 0X6A
    MEMORY_START = bytes([0x0F, 0xFF])
    controllers = []
    controllers.append('3ed08b')
    controllers.append('1c4e32')

    def __init__(self, command):
        self.command = command
        if len(command) < 5:
            self.isController = False
            return
        self.addr1 = command[2]
        self.addr2 = command[3]
        self.addr3 = command[4]
        self.deviceStr = self.getDeviceStr()
        self.isController = self.checkIfController()
        if self.isController:
            self.isHeld = self.checkIfHeld()
            self.wasReleased = self.checkIfReleased()
            self.buttonId = self.getButton()

#********************************* Initializer Methods ***************************************************#
    def getDeviceStr(self):
        byte_list = bytearray()
        byte_list.append(self.addr1)
        byte_list.append(self.addr2)
        byte_list.append(self.addr3)
        return Command.bToS(byte_list)

    def checkIfController(self):
        if self.deviceStr in self.controllers and len(Command.bToS(self.command)) == 22:
            return True
        return False

    def checkIfHeld(self):
        if self.command[9] == 0x17:
            return True
        return False

    def checkIfReleased(self):
        if self.command[9] == 0x18:
            return True
        return False

    def getButton(self):
        return self.command[7]
    
    
#********************************* Static Command Methods *************************************************#
    
    @staticmethod
    def bToS(byteString):
        return binascii.hexlify(byteString).decode('UTF-8') 
       
    @staticmethod
    def spaceOut(string):
        spacedStr = []
        for i in range(len(string)):
            spacedStr.append(string[i])
            if i % 2 == 1:
                spacedStr.append(' ')
        return ''.join(spacedStr)

    @staticmethod
    def sendMsg(msg):
        ser = SerialInstance().ser
        #print("MSG: %s" % Command.spaceOut(Command.bToS(msg)))
        ser.flushInput()
        ser.flushOutput()
        ser.write(msg)
        ser.flush()
    
    @staticmethod
    def sendCommand(device, cmd):
        msg = bytearray()
        msg.append(0x02) # INSTEON_PLM_START
        msg.append(0x62) # INSTEON_STANDARD_MESSAGE
        msg.extend(device)
        msg.append(0x0F) # INSTEON_MESSAGE_FLAG
        msg.append(cmd) # 0x12 = FAST ON, 0x14 = FAST OFF, 0x19 = STATUS
        msg.append(0xFF) # 0x00 = 0%, 0xFF = 100%
        Command.sendMsg(msg)
        
    @staticmethod
    def linkup():
        msg = bytearray()
        msg.append(0x02) # INSTEON_PLM_START
        msg.append(0x64) # INSTEON Start ALL-LINKING Command
        msg.append(0x01) # Link Code - Links IM as master
        msg.append(0x00) # All-Link Group
        Command.sendMsg(msg)
        
        
    @staticmethod
    def sendSetupCommand(cmd):
        if cmd == 0x60:
            print('\nSending IM Info...')
        elif cmd == Command.GET_FIRST_ALL_LINK:
            print('\nGetting first All-Link Record...')
        elif cmd == Command.GET_NEXT_ALL_LINK:
            print('\nGetting next All-Link Record')
        msg = bytearray()
        msg.append(0x02)
        msg.append(cmd)
        Command.sendMsg(msg)
        
    @staticmethod
    def queryALDB(device):
        msg = bytearray()
        msg.extend([0x02, 0x62])
        msg.extend(device)
        msg.extend([0x1F, 0x2F])
        for _ in range(15):
            msg.append(0x00)
        Command.sendMsg(msg)
        
    @staticmethod
    def queryMemory(device, memory):
        msg = bytearray()
        msg.extend([0x02, 0x62])
        msg.extend(device)
        msg.extend([0x1F, 0x2F])
        for _ in range(3):
            msg.append(0x00)
        msg.extend(memory)
        msg.append(0x01)
        for _ in range(9):
            msg.append(0x00)
        Command.sendMsg(msg)
        
    @staticmethod
    def groupRemoteLinc(device):
        msg = bytearray([0x02, 0x62])
        msg.extend(device)
        #Flags, Cmd1, Cmd2
        msg.extend([0x00, 0x0F, 0x00])
        
    