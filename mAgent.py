import subprocess
from  multiprocessing import Process
from flask import Flask, request
import sqlite3
import uuid
import time
from datetime import datetime
import configparser

runningTasks = []
app = Flask(__name__)

def runTask(taskID, serverCommand, serverCommandArgs, workingDir):
    command = '/home/brad/Code/mAgent/src/eaSupervisor.sh'
    #command = 'date'
    args = [str(taskID), workingDir, serverCommand, serverCommandArgs]
    #args = ['1', '/home/brad', 'date', '']
    
    task = (taskID, subprocess.Popen([command] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    runningTasks.append(task)
    print('Inserted Task')

def getPendingTasks():
    
    pendingTasks = executeQuery("SELECT TASK_ID, SERVER_COMMAND, SERVER_COMMAND_ARGS, WORKING_DIR FROM TASK_QUEUE WHERE TASK_STATUS LIKE ?", ('PENDING',))
    if len(pendingTasks) == 0:
       return None
    
    print(pendingTasks)
    return pendingTasks

def updateTaskStatus(taskID, status):
    executeQuery("UPDATE TASK_QUEUE SET STATUS = ? WHERE TASK_ID = ?", (status, taskID))

    
def executeQuery(sql, values):
    
    try:
        dbConn = sqlite3.connect('mAgentQueue.sqlite')
        cursor = dbConn.cursor()
        cursor.execute(sql, values)
        dbConn.commit()
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print("Error executing query:", e)
    finally:
        cursor.close()
        dbConn.close()

@app.route('/getAgentStatus', methods=['GET'])
def getAgentStatus():
    print('Server heartbeat response sent')
    return '', 205

@app.route('/getTaskStatus', methods=['POST'])
def getTaskStatus():
    print('Hello World')
    return 'Heyo', 200

@app.route('/taskInsert', methods=['POST'])
def insert_task():

    #Expected JSON Schema: 
    #{"taskID": 0, "taskCommand": "ls", "taskCommandArgs": "-l", "taskWorkingDir": "/home/brad"}

    taskID = None
    taskCommand = None
    taskCommandArgs = None
    postData = request.get_json()

    if 'taskID' not in postData:
        return 'You must supply a taskID', 500

    if 'taskCommand' not in postData:
        return 'You must supply a taskCommand', 500
    
    taskID = postData["taskID"]
    taskCommand = postData['taskCommand']
    taskCommandArgs = postData['taskCommandArgs']
    taskWorkingDir = postData['taskWorkingDir']

    sql = "INSERT INTO TASK_QUEUE (TASK_ID, SERVER_COMMAND, SERVER_COMMAND_ARGS, WORKING_DIR, TASK_STATUS) VALUES (?, ?, ?, ?, 'PENDING')"
    values = (taskID, taskCommand, taskCommandArgs, taskWorkingDir )

    executeQuery(sql, values)

    return 'Success', 200 

def taskManagerLoop():
    while True:
        time.sleep(1)
        print('Executing Task Loop...')
        #Launch Pending Tasks
        
        pendingTasks = getPendingTasks()
        if pendingTasks != None:
            for pendingTask in pendingTasks:
                ptaskID = pendingTask[0]
                pServerCommand = pendingTask[1]
                pServerCommandArgs = pendingTask[2]
                pWorkingDir = pendingTask[3]

                runTask(ptaskID, pServerCommand, pServerCommandArgs, pWorkingDir)

        #Poll status of running tasks
        if runningTasks:
            for taskID, taskProcess in runningTasks:
                taskReturnCode = taskProcess.poll()
                if taskReturnCode is not None: #Task has finished
                    taskOutput, taskError = taskProcess.communicate()
                    print(taskError.decode())
                    print(taskOutput.decode())
                    runningTasks.remove((taskID,taskProcess))
                    break
                else:
                    time.sleep(1)
                    continue


def writeLogEntry(msgClass, logText):
    curDate=datetime.now().strftime("%Y-%m-%d")
    curDateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logfilePath = f"log/EAgent.{curDate}.log"  
    if msgClass != 'DEBUG':
        with open(logfilePath, "a") as logFile:
            print(f'[{curDateTime} - {msgClass}] - {logText}')
            logFile.write(f'[{curDateTime} - {msgClass}] - {logText}\n')


if __name__ == "__main__":
    p = Process(target=taskManagerLoop) 
    p.start()
    app.run(debug=True, use_reloader=False)
    p.join()   






