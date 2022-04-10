#!/bin/bash

echo "0 11 * * * /usr/bin/docker run --rm -v /home/nathan/wordle_solver/logs:/app/logs -e DEBUG=false wordle_solver" 

