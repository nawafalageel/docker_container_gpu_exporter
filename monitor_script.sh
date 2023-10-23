#!/bin/bash

if pgrep -f "docker_gpu_exporter_v3.py" > /dev/null; then
    echo "The script is running."
else
    echo "The script is not running. Restarting..."
    # Add the command to restart your script here
   python3 /docker_container_gpu_exporter/docker_gpu_exporter_v3.py &
fi

