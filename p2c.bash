#!/bin/bash -e

c2p=$(docker ps | awk '{if (NR!=1) {print $1}}' | xargs -I {} docker inspect -f '{{.State.Pid}}' {})
# if [ $# -lt 1 ]
# then
#   echo "Usage:"
#   echo "   pid PID_1 ..."
  
#   exit 1
# fi
echo $c2p
my_pid=$c2p
echo $my_pid
p2c=$(docker ps --format "{{.Names}}" | awk '{print "echo name "$1"; docker top "$1}' | sh | awk -v PID="$my_pid" 'BEGIN{split(PID,pids," ")}{if (NF==2 && $1=="name") name=$2; for(pid in pids){pid=pids[pid];if (NF>2 && $2==pid) print "CONTAINER_NAME: "name"\nPID: "$2"\n"}}')
