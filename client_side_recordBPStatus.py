def myMac():
    from uuid import getnode as getMac
    mac = getMac()
    macString = ":".join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    return macString

def scanID():
    #initialize a list of tokens
    natID = []
    #scan the id
    print("Please scan ID")
    scanned = input()
    #parse the scanned string
    natID = scanned.split("~")
    counter = 0
    for i in natID:
        natID[counter]=i.replace("<", " ")
        counter+=1
    return [natID[5], natID[6], natID[4], natID[8], natID[9], natID[2].split(" ")[0]]

def captureVitals():
    import serial
    ser_port = serial.Serial ("/dev/ttyUSB0", baudrate = 9600, timeout = 1)
    vitals = []
    print('Please capture  BP vitals')

    while True:
        readings = ser_port.read(10).decode('ASCII')
        if readings == "":
            pass
        else:
            break
    vitals.append (int(readings[2] + readings[3], 16))
    vitals.append (int(readings[4] + readings[5], 16))
    vitals.append (int(readings[6] + readings[7], 16))

    return [vitals[0] + vitals[1], vitals[1], vitals[2]]
    
def composePayload():
    mac = myMac()
    demographics = scanID()
    vitals = captureVitals()
    payload = ""

    payload += demographics[0] + "|" + demographics[1] + "|" + demographics[2] + "|" + demographics[3] + "|" + demographics[4] + "|" + demographics[5] + "|" + str(vitals[0]) + "|" + str(vitals[1]) + "|" + str(vitals[2])  
    
    return payload

def sendSMS():
    pass

print(composePayload())
