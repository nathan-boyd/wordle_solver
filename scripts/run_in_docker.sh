#!/bin/bash

APP_DIR="$(pwd)"
echo $APP_DIR

docker run \
    -it \
    --rm \
    --env DEBUG=true \
    -v "$APP_DIR":/app \
    joyzoursky/python-chromedriver \
    /app/scripts/run.sh
