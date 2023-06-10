from eaEngine import eaEngine
from eaEndpoint import eaEndpoint
import requests

class eaTask:

    def __init__(self, taskID, scheduleID=None, instanceID=None, serverCommand=None, serverCommandArgs=None, workingDir=None,  status=None, endpointID=None, endpointUserID=None, effectiveDate=None) -> None:
        
        self.engine = eaEngine()

        if taskID == None:
            self.scheduleID = scheduleID
            self.instanceID = instanceID
            self.serverCommand = serverCommand
            self.serverCommandArgs = serverCommandArgs
            self.workingDir = workingDir
            self.status = status
            self.endpointID = endpointID
            self.endpointUserID = endpointUserID
            self.effectiveDate = effectiveDate
            
            #self.publishTask()
            #self.populateTaskID()
            return None
        
        sql = f"SELECT * FROM TASK WHERE ID = {taskID};"
        taskDefn = self.engine.executeQuery(sql)
    
        self.taskID = taskID
        self.scheduleID = taskDefn['schedule_id']
        self.instanceID = taskDefn['instance_id']
        self.serverCommand = taskDefn['server_command']
        self.serverCommandArgs = taskDefn['server_command_args']
        self.workingDir = taskDefn['working_dir']
        self.status = taskDefn['status']
        self.endpointID = taskDefn['endpoint_id']
        self.endpointUserID = taskDefn['endpoint_user_id']
        self.effectiveDate = taskDefn['effective_date']



    def populateTaskID(self):
        sql = f'''SELECT ID FROM TASK 
                  WHERE SCHEDULE_ID = {self.scheduleID} 
                  AND INSTANCE_ID = {self.instanceID} 
                  AND EFFECTIVE_DATE = '{self.effectiveDate}' '''
        
        taskID = self.engine.executeQuery(sql)
        print(taskID)
        self.taskID = taskID['id']
        return self.taskID

    def publishTask(self):
        DEFAULT_STATUS = 'SCHEDULED'
        sql = f'''INSERT INTO TASK (SCHEDULE_ID, INSTANCE_ID, EFFECTIVE_DATE, STATUS, ENDPOINT_ID, ENDPOINT_USER_ID, WORKING_DIR, SERVER_COMMAND, SERVER_COMMAND_ARGS)
                  VALUES ({self.scheduleID}, {self.instanceID}, '{self.effectiveDate}', '{DEFAULT_STATUS}', {self.endpointID}, {self.endpointID}, '{self.workingDir}', '{self.serverCommand}', '{self.serverCommandArgs}')'''
        self.engine.executeQuery(sql)
    
    def updateStatus(self, status):
        sql = f'''UPDATE TASK SET STATUS = '{status}' WHERE ID = {self.taskID};'''
        self.engine.executeQuery(sql)
    
    def launch(self):
        taskEndpoint = eaEndpoint(self.endpointID)
        if taskEndpoint.isActive == False:
            self.engine.writeLogEntry('WARNING', f'task.launch: endpoint {self.endpointID} is not active')

        if taskEndpoint.endpointType == 'wsgi':
            self.launchWSGI(taskEndpoint)

    def getJsonPayload(self) -> str:
        json = f'"taskID": {self.taskID}, "taskCommand": "{self.serverCommand}", "taskCommandArgs": "{self.serverCommandArgs}","taskWorkingDir": "{self.workingDir}"'
        jsonPayload = '{' + json + '}'
        return jsonPayload

    def launchWSGI(self, endpoint):
        self.updateStatus('LAUNCHED')

        jsonPayload = self.getJsonPayload()
        headers = {'Content-Type': 'application/json'}
        endpointAddress = endpoint.address
        url = f'http://{endpointAddress}/taskInsert'

        try: 
            response = requests.post(url, data=jsonPayload, headers=headers)
            if response.status_code == 200: 
                print('Task Inserted!!')
            return True
        except Exception as e:
            eaEngine.writeLogEntry('ERROR', f'launchWSGI: Error inserting task {jsonPayload} ' + str(e))
        return False

    def getOpenDeps(self):
        sql = f'''SELECT ID FROM TASK_DEPENDENCY WHERE TASK_ID = {self.taskID}'''
        openDeps = self.engine.executeQuery(sql)
        return openDeps

        





    