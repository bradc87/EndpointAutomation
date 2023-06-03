from flask import Flask, request
from multiprocessing import Process
from datetime import datetime
from eaEngine import eaEngine
from eaEndpoint import eaEndpoint
from eaTask import eaTask
import time

app = Flask(__name__)
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

def endpointStatusLoop():
    while True:
        time.sleep(LOOP_INTERVAL)
        engine = eaEngine()

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
        runnableTasks = getRunEligibleTasks()
        
        if runnableTasks != None:   
            for task in runnableTasks:
                task.launch()


if __name__ == "__main__":
    #print('generating tasks...')
    #generateTasks(1, '2023-06-02')

    epStatusLoop = Process(target=endpointStatusLoop)
    tlmLoop = Process(target=TLMLoop)
    epStatusLoop.start()
    tlmLoop.start()

    app.run(debug=True, use_reloader=False, port=8080)
    epStatusLoop.join()
    tlmLoop.join()
    

    