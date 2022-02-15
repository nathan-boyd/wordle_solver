#!/bin/bash

fswatch -o "$(pwd)/main.py" | xargs -n1 -I{} "$(pwd)/local_start.sh"
