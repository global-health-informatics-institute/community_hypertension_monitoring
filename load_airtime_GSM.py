import serial
import os, time

def load_airtime():
    # Enable Serial Communication
    ser_port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)

    # Delete all sms in GSM
    ser_port.write(str.encode('AT+cusd=1,"*136*_____________#"'+'\r\n'))            
    read_port = ser_port.read(10)
    time.sleep(0.1)

load_airtime()
