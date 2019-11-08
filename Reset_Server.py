import sqlite3
from sqlite3 import Error
import serial
import os, time


def clear_server_db():
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM demographic")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM Vitals")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM sms_TX_Q")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM sms_RX_Q")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM SIM")
    dbconnector.commit()

    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM Nodes")
    dbconnector.commit()

def delete_all_GSM():
    # Enable Serial Communication
    ser_port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=1)

    # Delete all sms in GSM
    ser_port.write(str.encode('AT+CMGDA="DEL ALL"'+'\r\n'))            
    read_port = ser_port.read(10)
    time.sleep(0.1)
    print("The Server Reset was Successful")

clear_server_db()
delete_all_GSM()        


