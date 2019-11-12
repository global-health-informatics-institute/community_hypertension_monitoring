import sqlite3

#Create a database connection to a disk file based database
dbConnector = sqlite3.connect("BP_server_db.db") 

# Obtain a cursor object
Cursor = dbConnector.cursor()

# Create a table in the disk file based database
create_table_sms_TX_Q = """CREATE TABLE sms_TX_Q(
        accession_No VARCHAR(20) PRIMARY KEY, 
        status VARCHAR(10) NOT NULL DEFAULT 'Pending',
        response text)"""

create_table_sms_RX_Q = """CREATE TABLE sms_RX_Q(
        sms_No INTEGER(5) NOT NULL, 
        Rec VARCHAR(10) NOT NULL,
        phone_No VARCHAR(15) NOT NULL,
        time_stamp DATETIME PRIMARY KEY NOT NULL,
        payload text)"""

create_table_demographic = """CREATE TABLE demographic(
        ID_No VARCHAR(12) PRIMARY KEY NOT NULL, 
        first_name VARCHAR(30) NOT NULL,
        last_name VARCHAR(30) NOT NULL,
        DOB DATETIME(15) NOT NULL,
        sex CHAR(1) NOT NULL,
        accession_No VARCHAR(20) NOT NULL,
        payload text)"""

create_table_sms_TX_Q = """CREATE TABLE sms_TX_Q(
        accession_No VARCHAR(20) PRIMARY KEY, 
        status VARCHAR(10) NOT NULL DEFAULT 'Pending',
        response text)"""


create_table_Vitals = """CREATE TABLE Vitals(
        sms_No INTEGER(5) NOT NULL, 
        time_stamp DATETIME NOT NULL DEFAULT current_timestamp UNIQUE,
        sys_mmHg INTEGER(3) NOT NULL,
	dia_mmHg INTEGER(3) NOT NULL,
	accession_No VARCHAR(20) PRIMARY KEY NOT NULL)"""

create_table_Nodes = """CREATE TABLE Nodes(
        mac_address VARCHAR(18) PRIMARY KEY NOT NULL,
	timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"""

create_table_SIM = """CREATE TABLE SIM(
        SIM_No VARCHAR(15) PRIMARY KEY NOT NULL,
        mac_address VARCHAR(18) NOT NULL,
        accession_No VARCHAR(20) NOT NULL,
        FOREIGN KEY (accession_No) REFERENCES Vitals(accession_No))"""

Cursor.execute(create_table_sms_TX_Q)
Cursor.execute(create_table_sms_RX_Q)
Cursor.execute(create_table_demographic)
Cursor.execute(create_table_Vitals)
Cursor.execute(create_table_Nodes)
Cursor.execute(create_table_SIM)
