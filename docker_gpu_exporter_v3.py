import time
import random
from os import path
import yaml
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
from prometheus_client import GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR
import subprocess

class CustomCollector(object):
    
    def __init__(self):
        # Run bash script
        self.results_dict = {"docker_container_running_gpu_pid": 0,
                "docker_container_name": "",
                "docker_container_used_gpu_id": 0,
                "docker_container_utilization_gpu_percent": 0,
                "docker_container_gpu_memory_used_MiB": 0,
                "docker_container_total_gpu_used": 0,
               }
        self.runnning_process = """PID: 423900
                            CONTAINER_NAME: containter_g03
                            GPU util: 0 423900 96 44 3 423900 92 44
                            GPU usage: 35383 MiB 35071 MiB


                            PID: 1572603
                            CONTAINER_NAME: container_kafka
                            GPU util: 0 1572603 - - 1 1572603 - -
                            GPU usage: 2307 MiB 7963 MiB


                            PID: 377944
                            CONTAINER_NAME: container_g1
                            GPU util: 1 377944 - -
                            GPU usage: 8001 MiB


                            PID: 2567679
                            CONTAINER_NAME: nemo
                            GPU util: 1 2567679 0 0
                            GPU usage: 2771 MiB


                            PID: 641061
                            CONTAINER_NAME: containter_g3
                            GPU util: 3 641061 - -
                            GPU usage: 2193 MiB



                            """
    def run_bash_script(self):
        return subprocess.run("./p2g.bash", stdout=subprocess.PIPE).stdout.decode('utf-8')
    
        
    def split_list(self, list_a, chunk_size):
        segmented_list = []
        for i in range(0, len(list_a), chunk_size):
            segmented_list.append(list_a[i:i + chunk_size])
        return segmented_list

    def parse_bash_results(self, runnning_process):
        multi_gpu_result_list = []
        for idx, container in enumerate(runnning_process.split("\n\n")):
            if not container:
                continue 
            elif len("".join(container.split(" ")))==0:
                continue
            elif "PID: " not in container:
                continue
            
            container_gpu_pid = container.split('PID: ')[1].split("\n")[0]
            container_name = container.split('CONTAINER_NAME: ')[1].split("\n")[0]
            container_gpu_util = container.split('GPU util: ')[1].split("\n")[0].split(' ')
            container_gpu_usage = container.split('GPU usage: ')[1].split("\n")[0].split(' ')

            if len(container_gpu_util) > 4:
                container_gpu_util = self.split_list(container_gpu_util, 4)
                container_gpu_usage = self.split_list(container_gpu_usage, 2)

                container_gpu_ids = list(list(zip(*container_gpu_util))[0])
                container_util_per_gpu = list(list(zip(*container_gpu_util))[3])
                container_usage_per_gpu = list(list(zip(*container_gpu_usage))[0])
                docker_container_total_gpu_used = len(container_gpu_util)
            else:
                container_gpu_ids = [container_gpu_util[0]]
                container_util_per_gpu = [container_gpu_util[3]]
                container_usage_per_gpu = [container_gpu_usage[0]]
                docker_container_total_gpu_used = len(container_gpu_util)//4

            for gpu_id, gpu_util, gpu_usage in zip(container_gpu_ids, container_util_per_gpu, container_usage_per_gpu):
                metrics_resutls = self.results_dict.copy()
                metrics_resutls["docker_container_running_gpu_pid"] = container_gpu_pid
                metrics_resutls["docker_container_name"] = container_name

                metrics_resutls["docker_container_used_gpu_id"] = gpu_id
                metrics_resutls["docker_container_utilization_gpu_percent"] = "0" if gpu_util=="-" else gpu_util
                metrics_resutls["docker_container_gpu_memory_used_MiB"] = gpu_usage
                metrics_resutls["docker_container_total_gpu_used"] = str(docker_container_total_gpu_used)
                multi_gpu_result_list.append(metrics_resutls)

        return multi_gpu_result_list


    def collect(self):
        labels=["container_name", "gpu"]
        
        for result_dict in self.parse_bash_results(self.run_bash_script()):
            container_name = str(result_dict["docker_container_name"])
            gpu_id = str(result_dict["docker_container_used_gpu_id"])

            gauge_pid = GaugeMetricFamily('docker_container_running_gpu_pid', 'What pid is the gpu container', labels=labels)
            gauge_pid.add_metric([container_name, gpu_id], value=int(result_dict['docker_container_running_gpu_pid']))
            yield gauge_pid

            gauge_name =  GaugeMetricFamily('docker_container_name', 'Container name', labels=labels)
            gauge_name.add_metric([container_name, gpu_id], value=1)
            yield gauge_name

            gauge_gpu_id =  GaugeMetricFamily('docker_container_used_gpu_id', 'Container used gpu', labels=labels)
            gauge_name.add_metric([container_name, gpu_id], value=int(result_dict['docker_container_used_gpu_id']))
            yield gauge_gpu_id

            gauge_util = GaugeMetricFamily('docker_container_utilization_gpu_percent', 'Help text', labels=labels)
            gauge_util.add_metric([container_name, gpu_id], value=int(result_dict['docker_container_utilization_gpu_percent']))
            yield gauge_util

            gauge_usage = GaugeMetricFamily('docker_container_gpu_memory_used_MiB', 'Help text', labels=labels)
            gauge_usage.add_metric([container_name, gpu_id], value=int(result_dict['docker_container_gpu_memory_used_MiB']))
            yield gauge_usage

            counter_gpu = CounterMetricFamily('docker_container_total_gpu_used', 'Help text', labels=labels)
            counter_gpu.add_metric([container_name, gpu_id], value=int(result_dict['docker_container_total_gpu_used']))
            yield counter_gpu


if __name__ == "__main__":
    port = 9066
    frequency = 0.5
    
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)
    start_http_server(port)
    REGISTRY.register(CustomCollector())
    while True: 
        # period between collection
        time.sleep(frequency)
