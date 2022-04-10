#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
APP_DIR="$(dirname "$SCRIPT_DIR")"

mkdir -p ./logs

docker build . -t wordle_solver

docker run -it --rm \
  -v $(pwd)/logs:/app/logs \
  -e DEBUG=true \
  wordle_solver:latest 
