
import os, time
import sqlite3
from sqlite3 import Error            
import serial   

# Enable Serial Communication
ser_port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.5)

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
        read_port = ser_port.read(10)
        #print (at_comm)

def delete_all_GSM():
    # Disable the Echo
    ser_port.write(str.encode('ATE0'+'\r\n'))                 
    read_port = ser_port.read(5)
    time.sleep(0.1)

    # Select Message format as Text mode 
    ser_port.write(str.encode('AT+CMGF=1'+'\r\n'))            
    read_port = ser_port.read(5)
    time.sleep(0.1)

    # Delete all sms in GSM
    ser_port.write(str.encode('AT+CMGDA="DEL ALL"'+'\r\n'))            
    read_port = ser_port.read(5)
    time.sleep(0.1)  

def add2DB(data=[]):
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    #create cursor to work with db
    Cursor = dbconnector.cursor()

    try:
        
        for i in range(1, len(data)):
            current_str = data[i].split(",")
            if len(current_str) > 1:
            #if current_str[1] == "\"REC UNREAD\"" or current_str[1] == "\"REC READ\"":
                global sms_nos
                sms_nos.append(current_str[0])
                splitted = current_str[5].split("\r",2)
                tstamp, payload = splitted[0], splitted[1]
                accession_No = payload.split("|")
                print(accession_No[0])
                SQL = "INSERT INTO sms_RX_Q(sms_No, Rec, phone_No, time_stamp, payload,accession_No) values(?,?,?,?,?,?)"
                data = (current_str[0], strip_quotes(current_str[1]), strip_quotes(current_str[2]), strip_quotes(current_str[4] + tstamp), payload, accession_No[0])
                print(SQL)
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
            

#======================================================================== PROCESS SMS BEGINS =========================================================================================

def process_sms():
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT  time_stamp,phone_No,payload FROM sms_RX_Q ORDER BY sms_No ASC")
    rows = Cursor.fetchall()

    #process payload
    for row in rows:
        time_stamp = row[0]     
        phone_No = row[1]   
        payload = row[2]        
        payload = row[2].split("|")     
        accession_No = payload[0].split("-")

        mac_address = accession_No[1]           
        accession_No = payload[0]   
        natID = payload[1]          
        first_name = payload[2]     
        last_name = payload[4]      
        sex = payload[5]            
        DOB = payload[6]            
        sys_mmHg = payload[7]       
        dia_mmHg = payload[8]       

        try:
            # moving records from sms_TX_Q table and insert them into other tables in db
            # delete processed records in sms_TX_Q
            
            if  len(payload) > 0 :

                #insert into demographic table
                Cursor.execute("INSERT INTO demographic(ID_No, first_name, last_name, DOB, sex,accession_No) VALUES(?, ?, ?, ?, ?, ?)",
                              (natID, first_name, last_name, DOB,sex, accession_No))
                dbconnector.commit()

                
                #insert into Vitals table
                Cursor.execute ("INSERT INTO Vitals(ID_No, time_stamp,sys_mmHg, dia_mmHg,accession_No) VALUES (?, ?,?, ?, ? )",
                                (natID, time_stamp, sys_mmHg, dia_mmHg,accession_No))
                dbconnector.commit()

                #insert into SIM table
                Cursor.execute ("INSERT INTO SIM(SIM_No, mac) VALUES (?, ? )",
                                (phone_No, mac_address))
                dbconnector.commit()

                #insert into Nodes table
                Cursor.execute ("INSERT INTO Nodes(mac_address, timestamp) VALUES (?, ? )",
                                (mac_address, time_stamp))
                dbconnector.commit()
                
                #delete processed sms
                Cursor.execute ("DELETE FROM sms_RX_Q WHERE time_stamp = \""+time_stamp+"\"")
                dbconnector.commit()

        except sqlite3.IntegrityError as e:
                print('sqlite error: ', e.args[0]) 

#================================================================================== COMPSE RESPONSE =================================================================================

def compose_response():   
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT first_name, last_name, accession_No FROM demographic ORDER BY ID_No ASC")
    rows = Cursor.fetchall()

    for row in rows:
        first_name = row[0]
        last_name = row[1]
        accession_No = row[2]
        print(accession_No)

        name = first_name + " " + last_name
        recommendation = "your Blood Pressure is not normal"
        response =accession_No+"|"+name +" " + recommendation 
        print(response)

        try:
            if len(response) > 0:
                Cursor.execute("INSERT INTO sms_TX_Q(accession_No, response) VALUES(?, ?)",
                            (accession_No,response))
                dbconnector.commit()
            
        except Error as er:
            print (" An error occured", er.args[0])

#================================================================================== SEND SMS =========================================================================================

def send_response():
    
    dbconnector = sqlite3.connect("BP_db.db")
    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT response,status FROM sms_TX_Q ORDER BY accession_No ASC")
    rows = Cursor.fetchall()

    for row in rows:
        response = row[0]
        retieved_status = row[1]
        #print(response)
        #print (retieved_status)
        
        if len(response) > 0 and retieved_status == 'Pending':
            # Sending a message to a particular Number
            ser_port.write(str.encode('AT+CMGS="+265885303568"'+'\r\n'))
            read_port = ser_port.read(5)
            #print (read_port)
            time.sleep(0.1)

            ser_port.write(str.encode(response))              
            #ser_port.write(str.encode('GSM Shield testing 9999999\r\n'))
            read_port = ser_port.read(1000)
            #print (read_port)
                
            # Enable to send SMS
            ser_port.write(str.encode("\x1A")) 
            read_port = ser_port.read(5)

            #updating the status of sms from pending to Sent after sending sms
            Cursor.execute ("UPDATE sms_TX_Q SET status = 'Sent' WHERE status = 'Pending'")
            dbconnector.commit()

        else:
            print ("Nothing to send")
            #pass

#====================================== clear sent responses from  the database ==================================================

def delete_sent_response():
    dbconnector = sqlite3.connect("BP_db.db")
    Cursor = dbconnector.cursor()
    Cursor.execute("DELETE FROM sms_TX_Q WHERE status = 'Sent'")
    rows = Cursor.fetchall()


while(True):
    ser_port.write(str.encode('AT+CMGL="ALL"\r\n'))
    read_port = ser_port.read(10000)
    print ("Checking sms in GSM...")
    time.sleep(0.1)
    #print(read_port)
    add2DB(tokenize(read_port.decode('utf-8')))
    
    process_sms()
    compose_response()
    send_response()
    delete_sent_response()
    delete_SMSs(sms_nos)
    sms_nos = []
    #delete_all_GSM()
    time.sleep(0.1)
            
        
