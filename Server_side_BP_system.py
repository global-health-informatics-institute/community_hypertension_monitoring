import serial
import RPi.GPIO as GPIO
import os, time


GPIO.setmode(GPIO.BOARD)

def find(str, ch):
    for i, ltr in enumerate(str):
        if ltr == ch:
            yield i

#connecting to serial port
ser_port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

# Disable the Echo
ser_port.write(str.encode('ATE0'+'\r\n'))                 
read_port = ser_port.read(10)
time.sleep(1)

# Select Message format as Text mode 
ser_port.write(str.encode('AT+CMGF=1'+'\r\n'))            
read_port = ser_port.read(10)
time.sleep(1)

# New SMS Message Indications
ser_port.write(str.encode('AT+CNMI=2,1,0,0,0'+'\r\n'))      
read_port = ser_port.read(10)
time.sleep(1)

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
        ser_port.read_port(10)
        #print (at_comm)
    

def add2DB(data=[]):
    import sqlite3
    from sqlite3 import Error
    
    #db connection
    dbconnector = sqlite3.connect("/home/pi/BP_project_database.db")

    #create cursor to work with db
    Cursor = dbconnector.cursor()

    for i in range(1, len(data)):
        current_str = data[i].split(",")
        if current_str[1] == "\"REC UNREAD\"" or current_str[1] == "\"REC READ\"":
            global sms_nos
            sms_nos.append(current_str[0])
            splitted = current_str[5].split("\r",2)
            tstamp, payload = splitted[0], splitted[1]
            payload = payload.split("\n")[1]
            print(payload)
            SQL = "INSERT INTO sms_queue(sms_No, Rec, phone, time_stamp, payload) values(?,?,?,?,?)"
            data = (current_str[0], strip_quotes(current_str[1]), strip_quotes(current_str[2]), strip_quotes(current_str[4] + tstamp), payload)
            print(SQL)
            print(data)
            #print(current_str[0])

            try:
                Cursor.execute(SQL, data)
                dbconnector.commit()
                print("=====")
                
            except Error as er:
                print("An error occured:", er.args[0])

            print("Data was sent to the database susccessfully!!!")

#Moving SMSs to db
while(True):
    #check inbox
    ser_port.write(str.encode('AT+CMGL="ALL"\r\n'))
    read_port = ser_port.read(10000)
    #os.system('clear')
    #time.sleep(1)
    print ("Running")
    time.sleep(5)
    print(read_port)
    add2DB(tokenize(read_port.decode('utf-8')))
    
    #clear read SMSs
    #sms_nos
    delete_SMSs(sms_nos)
    sms_nos = []

    #delay 2sec
    time.sleep(2)

    #recall the function
    #move_SMSs_to_db()

#start the recursive function
#move_SMSs_to_db()

