#!/bin/bash

crontab -l | { cat; echo "* 6 * * * /usr/bin/docker run --rm -v /home/nathan/wordle_solver/logs:/logs -e DEBUG=false wordle_solver"; } | crontab -
crontab -l

