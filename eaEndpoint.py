from eaEngine import eaEngine
import requests

class eaEndpoint: 
    def __init__(self, endpointID) -> None:
        
        self.engine = eaEngine()

        sql = f'''SELECT * FROM ENDPOINT WHERE ID = {endpointID}'''
        endpointDefn = self.engine.executeQuery(sql)

        if endpointDefn is None or len(endpointDefn) == 0:
            self.engine.writeLogEntry('WARNING', f'endpoint.init: cannot populate endpoint {endpointID}')
            pass

        self.endpointID = endpointDefn['id']
        self.displayName = endpointDefn['display_name']
        self.endpointType = endpointDefn['endpoint_type']
        self.address = endpointDefn['address']
        self.status = endpointDefn['status']
        self.enabled = endpointDefn['enabled']

    def isActive(self) -> bool:
        if self.status == 'online' and self.enabled == 'True':
            return True
        return False
    
    def checkStatus(self):
        if self.endpointType == 'wsgi':
            endpointStatus = self.checkStatusWSGI()
        
        if endpointStatus != True and self.status == 'online': 
            self.engine.writeLogEntry('WARNING', f'endpointStatusLoop: {self.address} has gone offline')
            self.status = 'offline'
            self.updateStatus('offline')
        elif endpointStatus == True and self.status == 'offline':
            self.engine.writeLogEntry('INFO', f'endpointStatusLoop: {self.address} has come online')
            self.status = 'online'
            self.updateStatus('online')

    def checkStatusWSGI(self):
        TIMEOUT_SECONDS = 5
        url = f'http://{self.address}/getAgentStatus' 
        try: 
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            if response.status_code == 205: 
                return True 
        except Exception as e:
            self.engine.writeLogEntry('DEBUG', f'getWSGIEndpointStatus: Error validating endpoint {self.address} : ' + str(e))
        return False
    
    def updateStatus(self, status):
        sql = f'''UPDATE ENDPOINT SET STATUS = '{status}' WHERE ID = {self.endpointID};'''
        if status == 'online':
            sql = f'''UPDATE ENDPOINT SET STATUS = '{status}', LAST_HEARTBEAT = NOW() WHERE ID = {self.endpointID};'''
            
        self.engine.executeQuery(sql) 



