import sqlite3

#Create a database connection to a disk file based database
dbConnector = sqlite3.connect("BP_client_db.db") 

# Obtain a cursor object
Cursor = dbConnector.cursor()

# Create a table in the disk file based database
create_table_sms_TX_Q = """CREATE TABLE sms_TX_Q(
        mac_address TEXT,
        sms_No INTEGER PRIMARY KEY ASC,
        payload TEXT,
        status TEXT,
        TTL_counter INTEGER,
        Time_Stamp DATETIME)"""

create_table_sms_RX_Q = """CREATE TABLE sms_RX_Q(
        accession_No Text PRIMARY KEY,
        status TEXT,Response)"""

Cursor.execute(create_table_sms_TX_Q)
Cursor.execute(create_table_sms_RX_Q)
