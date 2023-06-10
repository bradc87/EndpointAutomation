#!/usr/bin/env bash

# Script Title: eaRunner.sh
# Purpose: --
# Author: Brad Cunningham
# Dependencies: bash, curl, sqlite
# Changelog: 2023-05-23 - Initial Draft
set -x

# Globals
TaskID=$1
WorkingDir=$2
ServerCommand=$3
shift 3
CommandArgs=("$@")

SCRIPTPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGPATH="$SCRIPTPATH/output.txt"
DBFILE="$SCRIPTPATH/mAgentQueue.sqlite"
OUTPUTPATH="${SCRIPTPATH}/taskOutput"
OUTPUTFILE="${OUTPUTPATH}/${TaskID}.out"

#source agentConfig.ini

# Functions
updateTaskStatus() {
  local STATUS=$1

  if [ $STATUS == "SUCCESS" -o $STATUS == "FAILED" ]; then
    sql="UPDATE TASK_QUEUE SET TASK_STATUS = '${STATUS}', END_TIME = datetime('now') WHERE TASK_ID = ${TaskID}"
  elif [ $STATUS == "RUNNING" ]; then
    sql="UPDATE TASK_QUEUE SET TASK_STATUS = '${STATUS}', START_TIME = datetime('now')  WHERE TASK_ID = ${TaskID}"
  fi
  sqlite3 "$DBFILE" "$sql"
}

updateTaskOutput(){
  taskOutput=$(cat "$OUTPUTFILE")
  escapedTaskOutput=${taskOutput}
  sql="UPDATE TASK_QUEUE SET TASK_OUTPUT = '$escapedTaskOutput' WHERE TASK_ID = ${TaskID}"

  sqlite3 "$DBFILE" "$sql"
}

# Main Code
updateTaskStatus "RUNNING"
cd $WorkingDir
$ServerCommand ${CommandArgs[@]} > $OUTPUTFILE
ReturnCode=$?

if [ $ReturnCode -eq 0 ]; then
  updateTaskStatus "SUCCESS"
else
  updateTaskStatus "FAILED"
fi

updateTaskOutput

echo "ReturnCode = ${ReturnCode}"
