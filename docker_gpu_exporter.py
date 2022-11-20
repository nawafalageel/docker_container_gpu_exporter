import subprocess

def get_running_process():

    rc = subprocess.run("./p2g.bash", stdout=subprocess.PIPE)
    running_processes = rc.stdout.decode('utf-8')
    print(running_processes)
    return running_processes
