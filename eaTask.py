from eaEngine import eaEngine

class task:
    def __init__(self) -> None:
        pass

    def __init__(self, taskID) -> None:
        pass

    def __init__(self, taskID, scheduleID, instanceID, serverCommand, serverCommandArgs, workingDir,  status, endpointID, endpointUserID, effectiveDate) -> None:
        self.taskID = taskID
        self.scheduleID = scheduleID
        self.instanceID = instanceID
        self.serverCommand = serverCommand
        self.serverCommandArgs = serverCommandArgs
        self.workingDir = workingDir
        self.status = status
        self.endpointID = endpointID
        self.endpointUserID = endpointUserID
        self.effectiveDate = effectiveDate
        
        self.engine = eaEngine()
        pass

    def publishTask(self):
        DEFAULT_STATUS = 'SCHEDULED'
        sql = f'''INSERT INTO TASK (ID, SCHEDULE_ID, INSTANCE_ID, EFFECTIVE_DATE, STATUS, ENDPOINT_ID, ENDPOINT_USER_ID, WORKING_DIR, SERVER_COMMAND, SERVER_COMMAND_ARGS)
                  VALUES ({self.taskID},{self.scheduleID}, {self.instanceID}, '{self.effectiveDate}', '{DEFAULT_STATUS}', {self.endpointID}, {self.endpointID}, {self.workingDir}, '{self.serverCommand}', '{self.serverCommandArgs}')'''
        
        self.engine.executeQuery(sql)
    
    def updateStatus(self, status):
        sql = f'''UPDATE TASK SET STATUS = '{status}' WHERE ID = {self.taskID};'''
        self.engine.executeQuery(sql)

    def isEndpointActive(self) -> bool:
        sql = f'''SELECT STATUS FROM ENDPOINT WHERE ID = {self.endpointID} AND ENABLED IS True'''
        endpointStatus = self.engine.executeQuery(sql)

        if endpointStatus[0]['status'] == 'online':
            return True
        return False
    
    def launch(self):
        if self.isEndpointActive == False:
            self.engine.writeLogEntry('WARNING', f'task.launch: endpoint {self.endpointID} is not active')




    