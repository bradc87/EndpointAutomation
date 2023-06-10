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
        
        if sql.strip().upper().startswith("INSERT"):
            connection.commit()
            return None  # Return None for update queries
        
        results = cursor.fetchall()
        connection.commit()
        return results
    except psycopg2.Error as e:
        print(sql)
        print("Error executing query:", e)
    finally:
        cursor.close()
        connection.close()

def getEnabledEndpoints():
    sql = '''SELECT ID, DISPLAY_NAME, ADDRESS, STATUS FROM ENDPOINT WHERE ENABLED = TRUE;'''
    endpointList = executeQuery(sql)
    print(endpointList)
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

def isEndpointActive(endpointID):
    sql = f'''SELECT STATUS FROM ENDPOINT WHERE ID = {endpointID};'''
    endpointStatus = executeQuery(sql)
    if endpointStatus[0]['status'] == 'online':
        return True
    else:
        return False

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

def createTaskEntry(scheduleID, instanceID, effectiveDate, endpointUserID, workingDir, serverCommand, serverCommandArgs):
    DEFAULT_STATUS = 'SCHEDULED'
    sql = f'''INSERT INTO TASK (SCHEDULE_ID, INSTANCE_ID, EFFECTIVE_DATE, STATUS, ENDPOINT_USER_ID, WORKING_DIR, SERVER_COMMAND, SERVER_COMMAND_ARGS)
              VALUES ({scheduleID}, {instanceID}, '{effectiveDate}', '{DEFAULT_STATUS}', {endpointUserID}, '{workingDir}', '{serverCommand}', '{serverCommandArgs}')
           '''
    executeQuery(sql)

def getScheduleDefnDict(scheduleID):

    sql = f'''SELECT SERVER_COMMAND, SERVER_COMMAND_ARGS, RUN_USER_ID, WORKING_DIR, CALENDAR_ID, ENDPOINT_ID FROM SCHEDULE_DEFN WHERE SCHEDULE_ID = {scheduleID} AND ENABLED = True'''
    scheduleDefnDict = executeQuery(sql)

    if scheduleDefnDict is None:
        writeLogEntry('WARNING', f'getScheduleDefnDict: no schedule defn found for {scheduleID}')
        return None

    print(scheduleDefnDict[0]['server_command'])
    #serverCommand = scheduleDefnDict[1]['server_command']
    return scheduleDefnDict

def getTaskDict(scheduleID, instanceID, EffectiveDate):
    sql = f'''SELECT * FROM TASK 
               WHERE SCHEDULE_ID = {scheduleID} 
                 AND INSTANCE_ID = {instanceID} 
                 AND EFFECTIVE_DATE = '{EffectiveDate}';'''
    taskDict = executeQuery(sql)
    if taskDict is None:
        return None

    return taskDict[0]


def getLastTaskStatusDict(scheduleID, effectiveDate):
    sql = f'''SELECT INSTANCE_ID, STATUS FROM TASK WHERE DATE_TRUNC('day', EFFECTIVE_DATE) = '{effectiveDate}' AND SCHEDULE_ID = {scheduleID} '''
    rawStatus = executeQuery(sql)   
    if rawStatus is None:
        #return tuple of (lastInstanceID, lastStatus)
        lastTaskStatusDict={"lastInstanceID" : 0, "lastStatus" :  0}
    else:
        #Handle actual values here, maybe get the sql to create the dict in desired format
        lastTaskStatusDict={"lastInstanceID" : 0, "lastStatus" :  0}

    return lastTaskStatusDict

def generateTasks(scheduleID, effectiveDate):
    lastTaskStatus = getLastTaskStatusDict(scheduleID, effectiveDate)
    scheduleDefnDict = getScheduleDefnDict(scheduleID)

    if scheduleDefnDict is None:
        return
    
    if lastTaskStatus['lastStatus'] in (0,'Success'):
        lastInstanceID = lastTaskStatus['lastInstanceID']
        nextInstanceID = lastInstanceID + 1
    else: 
        writeLogEntry('WARNING', f'generateTasks: Attempted to create a task where one already exists {scheduleID}')
        return
        
    endpointID = scheduleDefnDict[0]['endpoint_id']
    endpointUserID = scheduleDefnDict[0]['run_user_id']
    workingDir = scheduleDefnDict[0]['working_dir']
    serverCommand = scheduleDefnDict[0]['server_command']
    serverCommandArgs = scheduleDefnDict[0]['server_command_args']

    createTaskEntry(scheduleID, nextInstanceID, effectiveDate, endpointUserID, workingDir, serverCommand, serverCommandArgs)

def getRunEligibleTasks():
    
    sql = '''SELECT SCHEDULE_ID, INSTANCE_ID FROM TASK WHERE STATUS IN ('SCHEDULED', 'WAITING ON DEPENDENCY', 'WAITING ON RESOURCE') '''
    eligibleTasks = executeQuery(sql)
    runnableTasks = []

    if eligibleTasks is None:
        return None

    for task in eligibleTasks: 
        taskScheduleID = task['schedule_id']
        taskInstanceID = task['instance_id']

        selectOpenDepsByTaskIDSQL = f'''SELECT ID FROM TASK_DEPENDENCY WHERE TASK_SCHEDULE_ID = {taskScheduleID} AND TASK_INSTANCE_ID = {taskInstanceID} AND STATUS LIKE 'OPEN';'''
        openDeps = executeQuery(selectOpenDepsByTaskIDSQL)
        if len(openDeps) == 0:
            runnableTasks.append({"scheduleID": taskScheduleID, "instanceID": taskInstanceID})

    return runnableTasks

def getEndpointDict(endpointID):
    sql = f'''SELECT * FROM ENDPOINT WHERE ID = {endpointID};'''
    endpointDict = executeQuery(sql)

    if endpointDict is None: 
        writeLogEntry('WARNING', f'getEndpointDict: Couldn\'t look up endpoint with ID {endpointID}')
        return None
    return endpointDict[0]

def updateTaskStatus(taskScheduleID, taskInstanceID, taskEffectiveDate, status):
    sql = f'''UPDATE TASK SET STATUS = '{status}' WHERE SCHEDULE_ID = {taskScheduleID} AND INSTANCE_ID = {taskInstanceID} AND EFFECTIVE_DATE = '{taskEffectiveDate}';'''
    try:
        executeQuery(sql)
    except psycopg2.Error as e:
        print("Error executing query:", e)
    


def launchTaskWSGI(taskDict, endpointDict):
    endpointID = endpointDict['id']
    endpointAddress = endpointDict['address']
    taskID = taskDict['id']
    taskScheduleID = taskDict['schedule_id']
    taskInstanceID = taskDict['instance_id']
    taskEffectiveDate = taskDict['effective_date']
    taskServerCommand = taskDict['server_command']
    taskServerCommandArgs = taskDict['server_command_args']

    if isEndpointActive(endpointID) is False: 
        writeLogEntry('WARNING', f'launchTaskWSGI: Tried to launch task where endpoint is not active: {endpointID}')
        return None 
    
    updateTaskStatus(taskScheduleID, taskInstanceID, taskEffectiveDate, 'Launched')
    
    json = f'"taskID": {taskID}, "taskCommand": "{taskServerCommand}", "taskCommandArgs": "{taskServerCommandArgs}"'
    json_payload = '{' + json + '}'

    headers = {'Content-Type': 'application/json'}
    timeout_seconds = 5
    url = f'http://{endpointAddress}/taskInsert' 
    try: 
        response = requests.post(url, data=json_payload, headers=headers)
        if response.status_code == 200: 
            print('Task Inserted!!')
            return 1 
    except Exception as e:
        writeLogEntry('DEBUG', f'getWSGIEndpointStatus: Error validating endpoint {endpointAddress} : ' + str(e))
    return 0


    
    #Check if endpoint is active 
    #Set status to launched 
    #insert task according to endpoint needs 



def launchTask(scheduleID, instanceID, effectiveDate):
    taskDict = getTaskDict(scheduleID, instanceID, effectiveDate)

    if taskDict is None: 
        writeLogEntry('WARNING', f'launchTask: Couldn\'t look up task with IDs {scheduleID}, {instanceID}, {effectiveDate}')
        return None

    taskEndpointID = taskDict['endpoint_id']
    endpointDict = getEndpointDict(taskEndpointID)

    if endpointDict is None:
        writeLogEntry('WARNING', f'launchTask: Couldn\'t look up endpoint with ID {taskEndpointID}')
        return None
    
    endpointType = endpointDict['endpoint_type']

    if endpointType == 'wsgi':
        launchTaskWSGI(taskDict, endpointDict)


def TLMLoop():
    while True:
        time.sleep(10)
        print('Getting Tasks')
        tasksToLaunch = getRunEligibleTasks()
        


        if tasksToLaunch is not None: 
            for task in tasksToLaunch:
                print('launching')
                launchTask(task['scheduleID'], task['instanceID'], '2023-06-02')

        


if __name__ == "__main__":
    #print('generating tasks...')
    #generateTasks(1, '2023-06-02')

    epStatusLoop = Process(target=endpointStatusLoop)
    epStatusLoop.start()
    tlmLoop = Process(target=TLMLoop)
    tlmLoop.start()
    app.run(debug=True, use_reloader=False, port=8080)
    epStatusLoop.join()
    tlmLoop.join()
    time.sleep(20)
    

    