from flask import Flask, request
from multiprocessing import Process
import time
from datetime import datetime
import psycopg2
import psycopg2.extras
import requests
import configparser

app = Flask(__name__)

LOOP_INTERVAL=10

def executeQuery(sql): 
    connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="EADev",
            user="brad",
            password=""
        )

    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)
    try:
        cursor.execute(sql)
        if sql.strip().upper().startswith("UPDATE"):
            connection.commit()
            return None  # Return None for update queries
        
        results = cursor.fetchall()
        connection.commit()
        return results
    except psycopg2.Error as e:
        print("Error executing query:", e)
    finally:
        cursor.close()
        connection.close()

def getEnabledEndpoints():
    sql = '''SELECT ID, DISPLAY_NAME, ADDRESS, STATUS FROM ENDPOINT WHERE ENABLED = TRUE;'''
    endpointList = executeQuery(sql)
    return endpointList

def updateEndpointStatus(agentID, status):
    if status == 'online':
        sql = f'''UPDATE ENDPOINT SET LAST_HEARTBEAT = NOW() WHERE ID = {agentID};'''
        executeQuery(sql) 

    sql = f'''UPDATE ENDPOINT SET STATUS = '{status}' WHERE ID = {agentID};'''
    executeQuery(sql)

def writeLogEntry(msgClass, logText):
    curDate=datetime.now().strftime("%Y-%m-%d")
    curDateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logfilePath = f"log/EAMS.{curDate}.log"  
    if msgClass != 'DEBUG':
        with open(logfilePath, "a") as logFile:
            print(f'[{curDateTime} - {msgClass}] - {logText}')
            logFile.write(f'[{curDateTime} - {msgClass}] - {logText}\n')

def endpointStatusLoop():
    while True:
        time.sleep(LOOP_INTERVAL)

        try:    
            endpointList = getEnabledEndpoints()
        except Exception as e:
            writeLogEntry('ERROR', 'EndpointStatusLoop: Error retrieving endpoints: ' + str(e))
            return None
        
        if endpointList is None:
            writeLogEntry('WARNING', 'EndpointStatusLoop: No enabled endpoints ')
            return None
        
        for agent in endpointList:
            endpointID = agent['id']
            endpointAddress = agent['address']
            endpointLastStatus = agent['status']
            # Add logic here for additional endpoint types

            endpointStatus = getWSGIEndpointStatus(endpointAddress)

            if  endpointStatus != 1: 
                if endpointLastStatus == 'online':
                    writeLogEntry('WARNING', f'endpointStatusLoop: {endpointAddress} has gone offline')
                updateEndpointStatus(endpointID, 'offline')
                continue

            #endpointStatus == 1:
            if endpointLastStatus == 'offline':
                writeLogEntry('INFO', f'endpointStatusLoop: {endpointAddress} has come online')
            updateEndpointStatus(endpointID, 'online')            
            continue

def getWSGIEndpointStatus(endpointAddress):
    timeout_seconds = 5
    url = f'http://{endpointAddress}/getAgentStatus' 
    try: 
        response = requests.get(url, timeout=timeout_seconds)
        if response.status_code == 205: 
            return 1 
    except Exception as e:
        writeLogEntry('DEBUG', f'getWSGIEndpointStatus: Error validating endpoint {endpointAddress} : ' + str(e))
    return 0

if __name__ == "__main__":
    epStatusLoop = Process(target=endpointStatusLoop)
    epStatusLoop.start()
    app.run(debug=True, use_reloader=False, port=8080)
    epStatusLoop.join()





