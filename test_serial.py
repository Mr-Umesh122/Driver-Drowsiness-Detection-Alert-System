import serial
import time

print(serial.__file__)  # DEBUG LINE

ser = serial.Serial('COM6', 115200)
time.sleep(2)

ser.write(b'A')
time.sleep(3)
ser.write(b'B')

ser.close()
