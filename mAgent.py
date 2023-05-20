import subprocess
from  multiprocessing import Process
from flask import Flask, request
import sqlite3
import uuid
import time

runningTasks = []
app = Flask(__name__)

def runTask(uuid, command):
    task = (uuid, subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    runningTasks.append(task)

def getPendingTasks():
    
    jobs = executeQuery("SELECT ID, SERVER_COMMAND FROM TASK_QUEUE WHERE STATUS LIKE ?", 'PENDING')
    print(jobs)

    #if len(jobs) == 0:
    #   return
    
def executeQuery(sql, values):
    dbConn = sqlite3.connect('mAgentQueue.sqlite')
    cursor = dbConn.cursor()
    try:
        cursor.execute(sql, values)
        dbConn.commit()
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print("Error executing query:", e)
    finally:
        cursor.close()
        dbConn.close()

@app.route('/getTaskStatus', methods=['POST'])
def getTaskStatus():
    print('Hello World')
    return 'Heyo', 200

@app.route('/insertTask', methods=['POST'])
def insert_task():

    taskID = None
    taskCommand = None
    postData = request.get_json()

    if 'taskID' not in postData:
        return 'You must supply a taskID', 500

    if 'taskCommand' not in postData:
        return 'You must supply a taskCommand', 500
    
    taskID = postData["taskID"]
    taskCommand = postData['taskCommand']

    sql = "INSERT INTO TASK_QUEUE (ID, SERVER_COMMAND, STATUS) VALUES (?, ?, 'PENDING')"
    values = (taskID, taskCommand)

    executeQuery(sql, values)
    return 'Success', 200 



def taskManagerLoop():

    runTask(1, './testScript1.sh')
    runTask(2, './testScript2.sh')
    
    while runningTasks:
        for taskID, taskProcess in runningTasks:
            taskReturnCode = taskProcess.poll()
            if taskReturnCode is not None: #Task has finished
                taskOutput, taskError = taskProcess.communicate()
                print(taskOutput.decode())
                runningTasks.remove((taskID,taskProcess))
                break
            else:
                time.sleep(1)
                continue

def commsLoop(): 
    while True:
        print('Getting Instructions')
        time.sleep(1)

if __name__ == "__main__":
    p = Process(target=commsLoop) 
    p.start()
    app.run(debug=True, use_reloader=False)
    p.join()   






