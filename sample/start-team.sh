#!/bin/bash
cd "$(dirname "$0")"

while true; do
    echo "[$(date)] Starting Agent Team..."
    python3 start.py

    if [ -f "restart.flag" ]; then
        rm -f restart.flag
        echo "[$(date)] Restart requested, restarting in 3s..."
        sleep 3
        continue
    fi

    echo "[$(date)] Stopped."
    break
done
