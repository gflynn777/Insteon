# Note: Set PLM to sync mode first followed by device sync
# Commands list: http://www.madreporite.com/insteon/commands.htm

import serial, binascii
from time import sleep
from Command import Command
startMsg = '\x02'

ser = serial.Serial(
                    port='COM4',
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=5
                    )

print("Starting alternate read method...")
while True:
    ser.flushInput()
    ser.flushOutput()
    
    st = ser.read()
    if (len(st) > 0):
        cmd = Command(st)
        print(cmd.bToS(st))


ser.close()