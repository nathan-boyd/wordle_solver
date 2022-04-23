#!/bin/bash

# this script runs as the start command in the docker image
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
APP_DIR="$(dirname "$SCRIPT_DIR")"

echo "starting xvfb"

Xvfb :1 -screen 0 1024x768x16 &> xvfb.log  &
sleep 1

echo "starting solver"

export DISPLAY=:1 && python3 "$APP_DIR/main.py"
