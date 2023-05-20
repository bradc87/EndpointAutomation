from flask import Flask, request
from multiprocessing import Process
import time
import psycopg2

app = Flask(__name__)

def executeQuery(sql): 
    connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="EADev",
            user="brad",
            password=""
        )

    cursor = connection.cursor()
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.commit()
        return results
    except psycopg2.Error as e:
        print("Error executing query:", e)
    finally:
        cursor.close()
        connection.close()
