# Note: Set PLM to sync mode first followed by device sync
# Commands list: http://www.madreporite.com/insteon/commands.htm

import binascii, atexit
from time import sleep
from Command import Command
from Device import Device, Scene
from Util import SerialInstance, Util

filename = 'deviceData.dat'

#Load data
savedObjList = Util.load_obj(filename)
if len(savedObjList) == 2:
    devices = savedObjList[0]
    scenes = savedObjList[1]
else:
    devices = {}
    scenes = {}
#Shutdown Hook
atexit.register(Util.save_obj, devices, scenes, filename)

def main():
    global devices
    
    for _, d in devices.items():
        d.printAldb()
    print('Device Total: %d' % len(devices))
    print(scenes['All Lights'].name)
    print(devices['265A46'].name)
    
    
    
def addDevice(name):
    global devices
    print('Adding device: %s' % Command.bToS(binascii.unhexlify(name)))
    devices[name] = Device(name)
    

def startListening():
    
    print("Starting to Read...")
    previousInput = b''
    
    
    while True:
        ser = SerialInstance().ser
        ser.flushInput()
        ser.flushOutput()
        x = '0'
        
        st = ser.readline()
        if (len(st) > 0 and st != previousInput):
            print(len(st))
            cmd = Command(st)
            print(Command.spaceOut(Command.bToS(st)))
            if cmd.isController == True:
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 1:
                    print('Turning lamp on...')
                    Command.sendCommand(ser, Device.MAIN_LAMP, Command.FAST_ON)
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 2:
                    print('Turning lamp off...')
                    Command.sendCommand(ser, Device.MAIN_LAMP, Command.FAST_OFF)
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 3:
                    Command.sendSetupCommand(ser, 0x69)
                    
                    while(x != '026a15'):
                        x = Command.bToS(ser.readline())
                        if (len(x) > 0):
                            print(x)
                        Command.sendSetupCommand(ser, Command.GET_NEXT_ALL_LINK)
                        sleep(.2)
                    print("out of loop")
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 4:
                    Command.sendSetupCommand(ser, Command.GET_NEXT_ALL_LINK)
                
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 5:
                    break
                
                if cmd.deviceStr == '3ed08b' and cmd.buttonId == 8:
                    Command.queryALDB(ser, Device.NEW_RLINC)
        
                            
    
        previousInput = st
    SerialInstance.close()
    
if __name__ == "__main__": main()
