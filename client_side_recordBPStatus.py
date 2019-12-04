import sqlite3
from sqlite3 import Error
import serial    
import os, time
from datetime import datetime

# Enable Serial Communication
ser_port = serial.Serial("/dev/ttyUSB_GSM", baudrate=9600, timeout=0.5)

server_Num = "+265886452444"

global mac_address

def myMac():
    from uuid import getnode as getMac
    mac = getMac()
    macString = ":".join(("%012X" % mac)[i:i+2] for i in range(0, 12,2))
    return macString

mac = myMac()

#============================================================ SEND SMS ====================================================================================


def send_sms():
    dbconnector = sqlite3.connect("/home/pi/BP_client.db")
    cursor = dbconnector.cursor()

    query = "SELECT payload, sms_No from sms_TX_Q WHERE status = 'Pending' LIMIT 0,1"
    cursor.execute(query)
    rows = cursor.fetchall()

    #retieving payload getting ready to send sms to the server  
    for row in rows:
        payload = row[0]
        sms_No = row[1]

        if len(payload) > 0 and sms_No > 0:
            cursor.execute ("UPDATE sms_TX_Q SET mac = \""+mac+"\" WHERE mac = 'not_set'")
            dbconnector.commit()

            #print (sms_No)
            accession_No = str(sms_No) +"-"+mac
            sms = accession_No + "|"+ payload

            cursor.execute ("UPDATE sms_TX_Q SET accession_No = \""+accession_No+"\" WHERE accession_No = 'not_set'")
            dbconnector.commit()

            # Sending a message to a particular Number
            ser_port.write(b'AT+CMGS="'+ server_Num.encode() + b'"\r\n')
            read_port = ser_port.read(5)
            #print (read_port)
            time.sleep(0.1)

            ser_port.write(str.encode(sms))              
            #ser_port.write(str.encode('GSM Shield testing 9999999\r\n'))
            read_port = ser_port.read(1000)
            print (read_port)
                    
            # Enable to send SMS
            ser_port.write(str.encode("\x1A"))
            #update status and sms_sent_time after sending smssend sms

            print ("Sent")
            update_query = "UPDATE sms_TX_Q SET status = 'Waiting' WHERE status = 'Pending'"
            cursor.execute(update_query)
            dbconnector.commit()            

            dt = datetime.now()
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    
            cursor.execute ("UPDATE sms_TX_Q SET sms_sent_time = \""+timestamp+"\" WHERE sms_sent_time = 'Null'")
            dbconnector.commit()

        else:
            pass

#=============================================================== RESEND SMS =======================================================================       

def resend_sms():
    dbconnector = sqlite3.connect("/home/pi/BP_client.db")
    cursor = dbconnector.cursor()

    status_query = "SELECT sms_No, payload, TTL_counter, sms_sent_time, accession_No from sms_TX_Q WHERE status ='Waiting'"
    cursor.execute(status_query)
    result_set = cursor.fetchall()
    for row in result_set:                 
        current_sms_No = row[0]
        data = row[1]
        TTL_counter = row[2]
        db_time = row[3]
        accession_No = row[4]
        payload = accession_No + "|" + data
        
        if db_time is "Null":
            pass

        else:
            db_time_splitted = db_time.split(" ")
            db_time_Only = db_time_splitted[1]
            #print(db_time_Only)
            h, m, s = db_time_Only.split(":")
            db_seconds_only = int(h) * 3600 + int(m) * 60 + int(s)
            now = datetime.now()
            c_time = now.strftime("%H:%M:%S")
            #print(c_time)
            new_current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            ch, cm, cs= c_time.split(":")
            c_time_seconds_only = int(ch) * 3600 + int(cm) * 60 + int(cs)
            check_time = c_time_seconds_only - db_seconds_only
            #check time if it is greater than delay time
            if check_time > 19:      
                if TTL_counter > 0:
                    new_TTL_counter = TTL_counter-1
                    cursor.execute("UPDATE sms_TX_Q SET TTL_Counter = ? WHERE sms_No = ?",[new_TTL_counter, current_sms_No])
                    dbconnector.commit()
                    # Sending a message to a particular Number
                    ser_port.write(str.encode('AT+CMGS="+265886452444"'+'\r\n'))
                    read_port = ser_port.read(5)
                    #print (read_port)
                    time.sleep(0.01)
                    ser_port.write(str.encode(payload))              
                    #ser_port.write(str.encode('GSM Shield testing 9999999\r\n'))
                    read_port = ser_port.read(1000)
                    print (read_port)
                    # Enable to send SMS
                    ser_port.write(str.encode("\x1A"))
                        
                else:
                    cursor.execute("UPDATE sms_TX_Q SET status = ? WHERE sms_No = ?",["Failed", current_sms_No])
                    dbconnector.commit()
            else:
                pass

#=================================================================== PROCESS RESPONSE FROM GSM ===============================================================

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
                #print(accession_No)
                #print(accession_No[1])
                SQL = "INSERT INTO sms_RX_Q(accession_No, response) values(?,?)"
                data = (accession_No[0], accession_No[1])
                delete_all_GSM()

                try:
                    Cursor.execute(SQL, data)
                    dbconnector.commit()
                    print("=====")
                    
                except Error as er:
                    #print("An error occured:", er.args[0])
                    pass
    except IndexError:
        pass

#======================================================================== loop ========================================================================
while(True):
    send_sms()
    resend_sms()
        
    #check inbox
    ser_port.write(str.encode('AT+CMGL="ALL"\r\n'))
    read_port = ser_port.read(10000)
   
    print ("Running...")
    time.sleep(0.1)
    
    add2DB(tokenize(read_port.decode('utf-8')))
        
    #delete_SMSs(sms_nos)
      
    time.sleep(0.1)
        
        





