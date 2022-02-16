#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
APP_DIR="$(dirname "$SCRIPT_DIR")"

pip3 install -r "$APP_DIR/requirements.txt"

export DEBUG=true && python3 "$APP_DIR/main.py"
