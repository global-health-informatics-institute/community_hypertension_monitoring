import os, time
import sqlite3
from sqlite3 import Error            
import serial
from datetime import datetime

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

                if len(accession_No) > 1:
                    #print(accession_No[0])
                    #print("TIMESTAMP")
                    #print (tstamp)
                    print ("sms received")
                    SQL = "INSERT INTO sms_RX_Q(sms_No, Rec, phone_No, time_stamp, payload,accession_No) values(?,?,?,?,?,?)"
                    data = (current_str[0], strip_quotes(current_str[1]), strip_quotes(current_str[2]), strip_quotes(current_str[4] + tstamp), payload, accession_No[0])
                    delete_all_GSM()
                    try:
                        Cursor.execute(SQL, data)
                        dbconnector.commit()
                        #print("=====")
                        
                    except Error as er:
                        #print("An error occured:", er.args[0])
                        pass

                else:
                    add2DB(tokenize(read_port.decode('utf-8')))

    except IndexError:
        pass

            

#============================================================================== PROCESS SMS ===================================================================================

def process_sms():
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT  time_stamp,phone_No,payload FROM sms_RX_Q ORDER BY sms_No ASC")
    rows = Cursor.fetchall()

    #moving records from sms_RX_Q table
    for row in rows:
        timestamp = row[0]
        phone =  row[1]
        payload = row[2]

        if len(payload) > 0:
            splitedPayload = payload.split("|")

            accession_No = splitedPayload[0]
            splited_accession_No = accession_No.split("-")

            mac = splited_accession_No[1]
            
            natID = splitedPayload[1]
            fName = splitedPayload[2]
            lName = splitedPayload[3]
            gender = splitedPayload[4]
            DOB = splitedPayload[5]
            BPsys = splitedPayload[6]
            BPdia = splitedPayload[7]

            try:
                # moving records from sms_RX_Q table and insert them into other tables in db
                # delete processed records in sms_RX_Q

                #insert into demographic table
                Cursor.execute("INSERT or IGNORE INTO demographic(ID_No, first_name, last_name, DOB, sex) VALUES(?, ?, ?, ?, ?)",
                                (natID, fName, lName, DOB,gender))
                dbconnector.commit()

                    
                #insert into Vitals table
                Cursor.execute ("INSERT or IGNORE INTO Vitals(ID_No, time_stamp,sys_mmHg, dia_mmHg,accession_No) VALUES (?, ?,?, ?, ? )",
                                (natID, timestamp, BPsys, BPdia,accession_No))
                dbconnector.commit()

                #insert into SIM table
                Cursor.execute ("INSERT or IGNORE INTO SIM(phone_No, mac_address, accession_No) VALUES (?, ?, ?)",
                                (phone, mac, accession_No))
                dbconnector.commit()

                #insert into Nodes table
                Cursor.execute ("INSERT or IGNORE INTO Nodes(mac_address, timestamp) VALUES (?, ? )",
                                (mac, timestamp))
                dbconnector.commit()
                    
                #delete processed sms
                Cursor.execute ("DELETE FROM sms_RX_Q WHERE time_stamp = \""+timestamp+"\"")
                dbconnector.commit()

            except sqlite3.IntegrityError as e:
                print('sqlite error: ', e.args[0])
                #pass
                

        else:
            pass


#======================================================================== COMPOSE RESPONSE =======================================================================================

def compose_response():
    
    #db connection
    dbconnector = sqlite3.connect("BP_db.db")

    #retrieve natID in first row
    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT ID_No FROM Vitals LIMIT 0,1")
    rows = Cursor.fetchall()

    natID = ""
    fName = ""
    lName = ""
    accession_No = ""
    current_BPsys = int()
    current_BPdia = int()
    previous_BPsys = int()
    previous_BPdia = int()
    
    for row in rows:
        natID = row[0]

        #print (natID)

    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT sys_mmHg, dia_mmHg, accession_No FROM Vitals WHERE ID_No = \""+natID+"\" ORDER BY time_stamp LIMIT 0,1")
    rows = Cursor.fetchall()

    recommendation = ""
    comment = ""
    reply = ""
    response = ""


    for row in rows:
            
        current_BPsys = row[0]
        current_BPdia = row[1]
        accession_No = row[2]

    #Response
    if current_BPsys > 1 and current_BPdia > 1:
                
        if (current_BPsys in range (100, 140)) and (current_BPdia in range (50, 90)):
            recommendation = " Your Blood pressure is normal"
            #print (recommendation)

        elif (current_BPsys in range (141, 160)) and (current_BPdia in range (91, 100)):
            recommendation = " See clinician within a month"
            #print (recommendation)

        elif (current_BPsys > 179) and (current_BPdia > 110):
            recommendation = " See clinician within a week"
            #print (recommendation)
        else:
            pass

    else:
        pass

    
    #Comparison
    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT sys_mmHg, dia_mmHg FROM Vitals WHERE ID_No = \""+natID+"\" ORDER BY time_stamp LIMIT 1,1")
    rows = Cursor.fetchall()
    for row in rows:
        if len(str(row[0])) < 1  or len(str(row[1])) < 1:
            pass

        else:
            previous_BPsys = row[0]
            previous_BPdia = row[1]


            if previous_BPsys > 1 and previous_BPdia > 1:
                
                if (previous_BPsys > current_BPsys) and (previous_BPdia > current_BPdia):
                    comment = " After comparing current with previous BP your BP has improved "
                    #print (comment)

                elif (previous_BPsys < current_BPsys) and (previous_BPdia < current_BPdia):
                    comment = " After comparing with current and previous BP your BP has not improved "
                    #print (comment)

                else:
                    pass

            else:
                pass


    #accessing name of a person in db using accession_No and add it to the response
    #used accession_No accessed from Vitals to access first_name and last_name in  demographic
    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT first_name, last_name FROM demographic WHERE ID_No = \""+natID+"\"")
    rows = Cursor.fetchall()

    for row in rows:
        fName = row[0]
        lName = row[1]

    reply = fName + " " + lName + " your current BP is " + str(current_BPsys) + "/" + str(current_BPdia)  + " your previous BP is " + str(previous_BPsys) + "/" + str(previous_BPdia) 
            
    response = accession_No + "|" + reply + " " + recommendation + comment    

    try:
        if len(response) > 60:
                
            Cursor.execute("INSERT INTO sms_TX_Q(accession_No, response) VALUES(?, ?)",
                        (accession_No,response))
            dbconnector.commit()
        else:
            pass
                    
    except Error as er:
            #print (" An error occured", er.args[0])
        pass


#=============================================================================== SEND SMS =====================================================================================================================

def send_response():
    
    dbconnector = sqlite3.connect("BP_db.db")
    Cursor = dbconnector.cursor()
    Cursor.execute("SELECT response,status, accession_No FROM sms_TX_Q")
    rows = Cursor.fetchall()

    for row in rows:
        response = row[0]
        status = row[1]
        accession_No = row[2]
        #print(accession_No)
        #print (retieved_status)
        
        if len(response) > 0 and status == 'Pending':
            
            Cursor = dbconnector.cursor()
            Cursor.execute("SELECT phone_No FROM SIM WHERE accession_No = \""+accession_No+"\"")
            rows = Cursor.fetchall()

            for row in rows:
                sim_No = row[0]
                #print(sim_No)
        
                # Sending a message to a particular Number
                ser_port.write(b'AT+CMGS="' + sim_No.encode() + b'"\r')
                read_port = ser_port.read(5)
                time.sleep(0.1)

                ser_port.write(str.encode(response))              
                read_port = ser_port.read(1000)
                time.sleep(0.1)
                print (read_port)
                    
                # Enable to send SMS
                ser_port.write(str.encode("\x1A")) 
                read_port = ser_port.read(5)

                print ("response sent")

                #updating the status of sms from pending to Sent after sending sms
                Cursor.execute ("UPDATE sms_TX_Q SET status = 'Sent' WHERE status = 'Pending'")
                dbconnector.commit()

                #delete sent response
                #Cursor.execute ("DELETE FROM sms_TX_Q WHERE status = 'Sent'")
                #dbconnector.commit()  

        else:
            pass


#================================================================================= LOOP ==================================================================================


while(True):
    ser_port.write(str.encode('AT+CMGL="ALL"\r\n'))
    read_port = ser_port.read(10000)
    print ("Running...")
    time.sleep(0.1)

    
    #print(read_port)
    add2DB(tokenize(read_port.decode('utf-8')))
    
    process_sms()
    compose_response()
    send_response()
    
    sms_nos = []
    time.sleep(0.1)
            
        
