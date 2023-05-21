from flask import Flask, request
from multiprocessing import Process
import time
from datetime import datetime
import psycopg2
import psycopg2.extras
import requests

app = Flask(__name__)

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

def updateAgentStatus(agentID, status):
    if status == 'online':
        sql = f'''UPDATE ENDPOINT SET LAST_HEARTBEAT = NOW() WHERE ID = {agentID};'''
        executeQuery(sql) 

    sql = f'''UPDATE ENDPOINT SET STATUS = '{status}' WHERE ID = {agentID};'''
    executeQuery(sql)

def writeLogEntry(msgClass, logText):
    curDate=datetime.now().strftime("%Y-%m-%d")
    logfilePath = f"log/{curDate}.txt"  
    
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")

def getEndpointStatus():
    timeout_seconds = 5

    try:    
        endpointList = getEnabledEndpoints()
    except Exception as e:
        print("Error getting enabled endpoints:", e)
        return None

    if endpointList is None:
        print("No enabled endpoints found.")
        return None

    for agent in endpointList:
        agentID = agent['id']
        agentAddress = agent['address']
        agentStatus = agent['status']

        url = f'http://{agentAddress}/getAgentStatus' 
        response = requests.get(url, timeout=timeout_seconds)

        if response.status_code == 205: 
            updateAgentStatus(agentID, 'online')
        else:
            updateAgentStatus(agentID, 'offline')

getEndpointStatus()
