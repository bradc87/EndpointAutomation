from flask import request, render_template
from eaMasterScheduler import app
from multiprocessing import Process
from datetime import datetime
from eaMasterScheduler.eaEngine import eaEngine
from eaMasterScheduler.eaEndpoint import eaEndpoint
from eaMasterScheduler.eaTask import eaTask
import time

#app = Flask(__name__, static_folder='static')
LOOP_INTERVAL=10

def getEnabledEndpoints():
    sql = '''SELECT ID FROM ENDPOINT WHERE ENABLED = TRUE;'''
    engine = eaEngine()
    endpointList = engine.executeQuery(sql)
    return endpointList

def getRunEligibleTasks(): 
    sql = '''SELECT ID FROM TASK WHERE STATUS IN ('SCHEDULED', 'WAITING ON DEPENDENCY', 'WAITING ON RESOURCE') '''
    engine = eaEngine()
    eligibleTaskIDs = engine.executeQuery(sql)
    runnableTasks = []

    if eligibleTaskIDs is None:
        return None

    for taskID in eligibleTaskIDs: 
        task = eaTask(taskID)

        if task.getOpenDeps() == None:
            print('no deps')
            runnableTasks.append(task)

    return runnableTasks

def getTaskByScheduleID(scheduleID, effectiveDate):

    sql = f'''SELECT ID FROM TASK WHERE SCHEDULE_ID = {scheduleID} AND EFFECTIVE_DATE = '{effectiveDate}' '''
    engine = eaEngine()
    taskIDs = engine.executeQuery(sql)

    if taskIDs == None:
        return None

    tasks = []

    for taskID in taskIDs:
        task = eaTask(taskID)
        tasks.append(task)

    return tasks    

def getScheduleDefnByID(scheduleID):
    sql = f'''SELECT * FROM SCHEDULE_DEFN WHERE SCHEDULE_ID = {scheduleID}; '''
    engine = eaEngine()
    scheduleDefn = engine.executeQuery(sql)
    return scheduleDefn

def generateTasks(scheduleID, effectiveDate):
    hwmInstanceID = 0 
    existingTasks = getTaskByScheduleID(scheduleID, effectiveDate)

    if existingTasks != None:
        #handle this
        pass

    scheduleDefn = getScheduleDefnByID(scheduleID)

    if scheduleDefn == None: 
        engine = eaEngine()
        engine.writeLogEntry('ERROR', f'Lookup failed for schedule ID {scheduleID}')


    instanceID = hwmInstanceID + 1 
    serverCommand = scheduleDefn['server_command']
    serverCommandArgs = scheduleDefn['server_command_args']
    workingDir = scheduleDefn['working_dir']
    endpointID = scheduleDefn['endpoint_id']
    endpointUserID = scheduleDefn['run_user_id']
    status = 'SCHEDULED'

    task = eaTask(None, scheduleID, instanceID, serverCommand, serverCommandArgs, workingDir, status, endpointID, endpointUserID, effectiveDate)
    task.publishTask()
    print(task.populateTaskID())

  

def endpointStatusLoop():
    while True:
        time.sleep(LOOP_INTERVAL)
        engine = eaEngine()
        print('EPS')
        try:    
            enabledEndpoints = getEnabledEndpoints()
        except Exception as e:
            engine.writeLogEntry('ERROR', 'EndpointStatusLoop: Error retrieving endpoints: ' + str(e))
            return None
        
        if enabledEndpoints is None or len(enabledEndpoints) == 0:
            engine.writeLogEntry('WARNING', 'EndpointStatusLoop: No enabled endpoints ')
            return None
        
        endpointsToCheck=[]

        for endpoint in enabledEndpoints:
            ep = eaEndpoint(endpoint)
            endpointsToCheck.append(ep)
        
        for endpoint in endpointsToCheck:
            endpoint.checkStatus()

def TLMLoop():
    while True:
        time.sleep(LOOP_INTERVAL)
        print('TLM')
        runnableTasks = getRunEligibleTasks()
        
        if runnableTasks != None:   
            for task in runnableTasks:
                task.launch()

def startAppLoops():
    epStatusLoop = Process(target=endpointStatusLoop)
    tlmLoop = Process(target=TLMLoop)
    epStatusLoop.start()
    tlmLoop.start()

    app.run(debug=True, use_reloader=False, port=8080)

    epStatusLoop.join()
    tlmLoop.join()





  
    

    
