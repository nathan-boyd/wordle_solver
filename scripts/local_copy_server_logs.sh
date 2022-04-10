#!/bin/bash

FROM="/home/nathan/wordle_solver/logs/"
TO="$HOME/Desktop/storage/engineering/wordle_solver/"

echo "Copying Logs"
echo "    from: $FROM"
echo "    to:   $TO"

scp -r nathan@cloudbox:"$FROM" "$TO"
