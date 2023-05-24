#!/usr/bin/env bash

dbFile="mAgentQueue.sqlite"
sql="SELECT json_object('TASK_ID', TASK_ID, 'INSTANCE_ID', INSTANCE_ID, 'SERVER_COMMAND', SERVER_COMMAND, 'SERVER_COMMAND_ARGS', SERVER_COMMAND_ARGS ) FROM TASK_QUEUE"

result=$(sqlite3 "$dbFile" "$sql")
echo "$result"

