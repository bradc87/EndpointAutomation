#!/usr/bin/env bash

# Globals
TaskID=$1
InstanceID=$2
ServerCommand=$3
shift 3
CommandArgs=("$@")

INITIAL_STATUS="Pending"
SCRIPTPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DBFILE="mAgentQueue.sqlite"
sql="SELECT json_object('TASK_ID', TASK_ID, 'INSTANCE_ID', INSTANCE_ID, 'SERVER_COMMAND', SERVER_COMMAND, 'SERVER_COMMAND_ARGS', SERVER_COMMAND_ARGS ) FROM TASK_QUEUE"

insertTaskDetails(){
    echo "Inserting Task Details"
    sql="INSERT INTO TASK_QUEUE(TASK_ID, INSTANCE_ID, SERVER_COMMAND, SERVER_COMMAND_ARGS, TASK_STATUS, INSERT_TIME) VALUES (${TaskID}, ${InstanceID}, '${ServerCommand}', '${CommandArgs}', '${INITIAL_STATUS}', datetime('now'))"
    sqlite3 "$DBFILE" "$sql"
}

startTask(){
    echo "Starting Task..."
    cd $SCRIPTPATH
    nohup ./eaSupervisor.sh ${TaskID} ${InstanceID} ${ServerCommand} ${CommandArgs} &
    returnCode=$?
    echo ${returnCode}
}

insertTaskDetails
startTask
