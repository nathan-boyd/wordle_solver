#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
APP_DIR="$(dirname "$SCRIPT_DIR")"

Xvfb :1 -screen 0 1024x768x16 &> xvfb.log  &

python3 "$APP_DIR/main.py"

