import sqlite3
from sqlite3 import Error
import serial    
import os, time
from datetime import datetime

# Enable Serial Communication
ser_port = serial.Serial("/dev/ttyUSB2", baudrate=9600, timeout=0.5)

#======================================== SEND SMS ========================================================

def send_sms():
    dbconnector = sqlite3.connect("/home/pi/BP_client.db")
    cursor = dbconnector.cursor()

    query = "SELECT payload from sms_TX_Q"
    cursor.execute(query)
    rows = cursor.fetchall()
        
    for row in rows:
        retrieved_list = row[0]
        data = ""
        data = retrieved_list
        #print(data)
        update_query = "UPDATE sms_TX_Q SET status = 'Waiting' WHERE status = 'Pending'"
        cursor.execute(update_query)
        dbconnector.commit()

        # Sending a message to a particular Number
        ser_port.write(str.encode('AT+CMGS="+265886452444"'+'\r\n'))
        read_port = ser_port.read(5)
        #print (read_port)
        time.sleep(0.1)

        ser_port.write(str.encode(data))              
        #ser_port.write(str.encode('GSM Shield testing 9999999\r\n'))
        read_port = ser_port.read(1000)
        print (read_port)
        
        # Enable to send SMS
        ser_port.write(str.encode("\x1A"))
        print ("Time sent")
        print  (datetime.now())

#====================================== PROCESS RESPONSE FROM GSM =================================

def find(str, ch):
    for i, ltr in enumerate(str):
        if ltr == ch:
            yield i

#initialize unread SMSs' index list
sms_nos = []

def strip_quotes(data = ""):
    length = len(data)
    new_string = ""
    for i in range(length):
        if i > 0 and i < length-1:
            new_string += data[i]
    return new_string


def tokenize(strng):
    strings = strng.split("\r\n+CMGL:")
    return strings

def delete_SMSs(sms_no = []):
    for i in range (len(sms_no)):
        at_comm = 'AT+CMGD = ' +sms_no[i] + '\r\n'
        ser_port.write(str.encode(at_comm))
        ser_port.read(10)
        #print (at_comm)

def delete_all_GSM():
    # Delete all sms in GSM
    ser_port.write(str.encode('AT+CMGDA="DEL ALL"'+'\r\n'))            
    read_port = ser_port.read(5)
    time.sleep(0.001)


def add2DB(data=[]):
    #db connection
    dbconnector = sqlite3.connect("/home/pi/BP_client.db")

    #create cursor to work with db
    Cursor = dbconnector.cursor()
    
    try:
            
        for i in range(1, len(data)):
            current_str = data[i].split(",")
            if len(current_str) > 0:
            #if current_str[1] == "\"REC UNREAD\"" or current_str[1] == "\"REC READ\"":
                global sms_nos
                sms_nos.append(current_str[0])
                splitted = current_str[5].split("\r",2)
                #print (current_str[5])
                response = splitted[1]
                response = response.split("\n")[1]
                print(response)
                accession_No = response.split("|")
                accession_No[0]
                print(accession_No)
                #print(accession_No[1])
                SQL = "INSERT INTO sms_RX_Q(accession_No, response) values(?,?)"
                data = (accession_No[0], accession_No[1])

                #print(SQL)
                #print(data)
                #print(current_str[0])

                try:
                    Cursor.execute(SQL, data)
                    dbconnector.commit()
                    print("=====")
                    
                except Error as er:
                    print("An error occured:", er.args[0])
    except IndexError:
        pass

#Moving SMSs to db
while(True):

    send_sms()
        
    #check inbox
    ser_port.write(str.encode('AT+CMGL="ALL"\r\n'))
    read_port = ser_port.read(10000)
    #os.system('clear')
    #time.sleep(1)
    print ("Checking sms in GSM...")
    time.sleep(0.1)
    #print(read_port)
    add2DB(tokenize(read_port.decode('utf-8')))
        
    #clear read SMSs
    #sms_nos
    #sms_nos = []

    #delay 2sec
    #time.sleep(1)

    #recall the function
    #move_SMSs_to_db()
    delete_SMSs(sms_nos)
    #delete_all_GSM()   
    time.sleep(0.1)
        
        





