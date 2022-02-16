#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "Script Dir $SCRIPT_DIR"
echo "App Dir $APP_DIR"

python3 -m pip install -r "$APP_DIR/requirements.txt"

export RUNNING_IN_CONTAINER=false DEBUG=true && python3 "$APP_DIR/main.py"
