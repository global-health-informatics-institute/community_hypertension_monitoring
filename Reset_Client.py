import sqlite3
from sqlite3 import Error
import serial
import os, time


def clear_client_db():
    #db connection
    dbconnector = sqlite3.connect("/home/pi/BP_client.db")

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM sms_TX_Q")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM sms_RX_Q")
    dbconnector.commit()


def delete_all_GSM():
    # Enable Serial Communication
    ser_port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)

    # Delete all sms in GSM
    ser_port.write(str.encode('AT+CMGDA="DEL ALL"'+'\r\n'))            
    read_port = ser_port.read(10)
    time.sleep(0.1)
    print("The Client Reset sas Successful")

    
clear_client_db()
delete_all_GSM()        


