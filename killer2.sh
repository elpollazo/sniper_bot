#!/bin/bash
#./killer2.sh <process_id>

processes=$(ps -aux | grep "buyer.py" | awk '{print $2}')

for process in $processes; do
    if [ $1 == $process ]; then
        echo '' >/dev/null
    else
        kill $process 2>/dev/null
    fi
done
