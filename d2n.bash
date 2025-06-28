#!/bin/bash -e

Help() {
    echo -e "Usage: $0 [options] <No options required>"
    echo -e ""
    echo -e "Options:"
    echo -e "  -h, --help     Show this help message"
    echo -e ""
    echo -e "Output columns:"
    echo -e "  PID             : PID that uses the GPU"
    echo -e "  CONTAINER_NAME  : Container name (if any)"
    echo -e "  GPU_ID          : GPU device ID"
    echo -e "  SM_UTIL         : SM utilization (%)"
    echo -e "  MEM_UTIL        : GPU memory utilization (%)"
    echo -e "  MEM_USED        : Memory used (MiB)"
}

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    Help
    exit 0
fi

my_pids=$(nvidia-smi | sed '1,/Processes:/d' | awk '{print $5}' | grep -v 'PID' | grep -v '|' | awk '!NF || !seen[$0]++')

echo -e "PID     CONTAINER_NAME       GPU_ID SM_UTIL MEM_UTIL MEM_USED"
echo -e "------ -------------------- ------ ------- -------- --------"


for pid in $my_pids; do
    p2g_util=$(nvidia-smi pmon -c 1 | grep " $pid " | awk '{print $1, $2, $4, $5}')
	
    p2g_usage=$(nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv | grep ", $pid," | awk -F',' '{gsub(/ /,"",$3); print $3}')
    container_name=$(docker ps --format "{{.Names}}" \
        | while read name; do
            if docker top "$name" | awk -v pid=$pid '$2==pid {print name; exit}'; then
                break
            fi
          done)

    read gpu_id _pid sm_util mem_util <<< "$p2g_util"
echo -e "$(printf "%-6s %-20s %-6s %-7s %-8s %-8s" "$pid" "$container_name" "$gpu_id" "$sm_util" "$mem_util" "$p2g_usage")"
done