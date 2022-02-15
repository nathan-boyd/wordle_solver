#!/bin/bash

mkdir -p ./logs

docker build . -t wordle_solver

docker run -it --rm \
  -v $(pwd)/logs:/logs \
  -e DEBUG=true \
  wordle_solver:latest
