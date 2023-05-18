import subprocess
from  multiprocessing import Process
import sqlite3
import uuid
import time

runningTasks = []

def runTask(uuid, command):
    task = (uuid, subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    runningTasks.append(task)

def getPendingTasks():
    dbConn = sqlite3.connect("mAgentQueue.sqlite")
    dbCursor = dbConn.execute("SELECT ID, SERVER_COMMAND FROM TASK_QUEUE WHERE STATUS LIKE 'PENDING")
    jobs = dbCursor.fetchall()

    if len(jobs) == 0:
        return

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
    p2 = Process(target=taskManagerLoop)
    p.start()
    p2.start()

    p.join()   
    p2.join()





