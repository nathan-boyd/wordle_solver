#!/bin/bash

APP_DIR="/home/nathan/wordle_solver"
LOGS_DIR="$APP_DIR/logs"
WORKING_DIR="$(pwd)"

mkdir -p $LOGS_DIR 

cd $APP_DIR 
/usr/bin/docker build . -t wordle_solver 

/usr/bin/docker run -it --rm \
  -v "$LOGS_DIR":/logs \
  -e DEBUG=true \
  wordle_solver:latest
