#!/bin/bash -e

container_names=$(docker ps --format "{{.Names}}")
for c_name in $container_names; do

  check_gpu=$(docker inspect $c_name | grep -q gpu)
  if $check_gpu; then
    p2g_util=$(docker exec -it $c_name nvidia-smi pmon -c 1 |  awk '{print $1, $2, $4, $5}')
    echo -e $p2g_util
    
    p2g_usage=$(docker exec -it $c_name nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv | awk '{print $3, $4}')
    
    echo -e $p2g_usage
  fi
done
