#!/usr/bin/env bash

#   Script Title: eaRunner.sh
#        Purpose: --
#         Author: Brad Cunningham
#   Dependancies: bash, curl, sqlite
#      Changelog: 2023-05-23 - Initial Draft



#Globals
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source agentConfig.ini

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <command> <command_args...>"
  exit 1
fi

command="$1"
shift
command_args=("$@")

"$command" "${command_args[@]}" > output.txt 2>&1
return_code=$?


exit "$return_code"