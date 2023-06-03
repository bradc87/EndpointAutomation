import psycopg2
import psycopg2.extras
import configparser
from datetime import datetime

class eaEngine:

    def __init__(self):
        configReader = configparser.ConfigParser()
        configReader.read('eaConfig.ini')

        #Database configuration
        self.dbHost = configReader.get('DEFAULT', 'dbHost')
        self.dbPort = configReader.get('DEFAULT', 'dbPort')
        self.dbDatabase = configReader.get('DEFAULT', 'dbDatabase')
        self.dbUser = configReader.get('DEFAULT', 'dbUser')
        self.dbPassword = configReader.get('DEFAULT', 'dbPassword')

        #Log configuration
        self.logPath = configReader.get('DEFAULT', 'logPath')

    def executeQuery(self, sql): 
        connection = psycopg2.connect(
                host = self.dbHost,
                port = self.dbPort,
                database = self.dbDatabase,
                user = self.dbUser,
                password = self.dbPassword)

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

            if len(results) == 0:
                return None
            elif len(results) == 1:
                results = results[0]
                
            return results
        except psycopg2.Error as e:
            print(sql)
            print("Error executing query:", e)
        finally:
            cursor.close()
            connection.close()
    
    def writeLogEntry(self, msgClass, logText):
        curDate=datetime.now().strftime("%Y-%m-%d")
        curDateTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logfilePath = f"{self.logPath}EAMS.{curDate}.log"  
        if msgClass != 'DEBUG':
            with open(logfilePath, "a") as logFile:
                print(f'[{curDateTime} - {msgClass}] - {logText}')
                logFile.write(f'[{curDateTime} - {msgClass}] - {logText}\n')