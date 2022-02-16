#!/bin/bash

FROM="/home/nathan/wordle_solver/logs/2022-02-16/"
TO="$HOME/Desktop/storage/engineering/wordle_solver_logs/"

echo "Copying Logs"
echo "    from: $FROM"
echo "    to:   $TO"

scp -r nathan@cloudbox:"$FROM" "$TO"
