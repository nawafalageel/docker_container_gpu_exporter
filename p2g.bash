#!/bin/bash -e

my_pids=$(nvidia-smi | sed '1,/Processes:/d' | awk '{print $5}' | grep -v 'PID' | grep -v '|' | awk '!NF || !seen[$0]++')

for pid in $my_pids; do
	p2g_util=$(nvidia-smi pmon -c 1 | grep $pid | awk '{print $1, $2, $4, $5}')
	#echo -e $p2g_util
    	p2g_usage=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv | grep $pid | awk '{print $3, $4}')
	#echo -e $p2g_usage
	p2c=$(docker ps --format "{{.Names}}" | awk '{print "echo name "$1"; docker top "$1}' | sh | awk -v PID="$pid" 'BEGIN{split(PID,pids," ")}{if (NF==2 && $1=="name") name=$2; for(pid in pids){pid=pids[pid];if (NF>2 && $2==pid) print "CONTAINER_NAME: "name"\n"}}')
	if [ ! -z "$p2c" ]
	then
		echo -e PID: $pid
		echo -e $p2c
		echo -e GPU util: $p2g_util
		echo -e GPU usage: $p2g_usage 
		echo -e "\n"
	else
		echo -e "\n"
	fi
done
