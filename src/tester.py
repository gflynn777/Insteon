import serial, binascii
from time import sleep
from Command import Command

ser = serial.Serial(
                    port='COM4',
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=0.02
                    )

print("LED OFF")
ser.flushInput()
ser.flushOutput()
msg = bytearray()
msg.append(0x02)
msg.append(0x6E)
ser.write(msg)
ser.flush()