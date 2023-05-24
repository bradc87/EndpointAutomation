#!/usr/bin/env bash

# Script Title: eaRunner.sh
# Purpose: --
# Author: Brad Cunningham
# Dependencies: bash, curl, sqlite
# Changelog: 2023-05-23 - Initial Draft

# Globals
SCRIPTPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGPATH="$SCRIPTPATH/output.txt"
DBFILE="mAgentQueue.sqlite"

source agentConfig.ini

TaskID=$1
InstanceID=$2
ServerCommand=$3

# Functions
writeTaskDetails() {
  echo "Nope"
}

updateTaskStatus() {
  local STATUS=$1
  sql="UPDATE TASK_QUEUE SET TASK_STATUS = '${STATUS}' WHERE TASK_ID = ${TaskID} AND INSTANCE_ID = ${InstanceID}"
  sqlite3 "$DBFILE" "$sql"
}

shift 3
CommandArgs=("$@")

"$ServerCommand" "${CommandArgs[@]}" >$LOGPATH
ReturnCode=$?

if [ $ReturnCode -eq 0 ]; then
  updateTaskStatus "Success"
else
  updateTaskStatus "Failed"
fi

echo "ReturnCode = ${ReturnCode}"
