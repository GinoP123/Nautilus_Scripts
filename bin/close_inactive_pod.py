#!/usr/bin/env python3

import sys
import subprocess as sp
import requests
import re
import os
import time
import settings
import ast

pod_name = sys.argv[1]
port = settings.config['port']

### Checking if Pod Exists

check_pod_exists = f"kubectl describe pod {pod_name}"
pod_description = sp.run(check_pod_exists, 
       capture_output=True, shell=True).stdout.decode()

if pod_description == '' or not pod_name.strip():
    print("Error: Pod Not Found")
    exit(1)


### Checking if Active Port Forwarding

command = f"sudo lsof -i :{port} -P -n | grep ESTABLISHED"
check_active_connections = f"kubectl exec -it {pod_name} -- /bin/bash"
check_active_connections += f" -c '{command}'"

active_connections = sp.run(check_active_connections, 
                            shell=True, 
                            capture_output=True).stdout.decode()

if active_connections.strip() != '':
    print("Active Port Connections Found (Pod Is In Use)")
    print("Exiting Without Deleting Pod")
    exit(2)


### Opening New Port Forwarding

port_forward_command = f"kubectl port-forward {pod_name} {port}:{port}"
port_forward_job = sp.Popen(port_forward_command, shell=True)

valid_connection = False
while not valid_connection:
    try:
        requests.get(f'http://localhost:{port}')
        valid_connection = True
    except requests.exceptions.ConnectionError:
        print('Waiting for Port Forwarding Connection')
        time.sleep(1)


### Checking for Active Jupyter Kernels

kernel_api = f'http://localhost:{port}/api/kernels'
notebook_status = ast.literal_eval(requests.get(kernel_api).text)
running_notebook = any(x['execution_state'] == 'busy' for x in notebook_status)
port_forward_job.kill()

if running_notebook:
    print("Active Jupyter Notebook Kernel Running")
    print("Exiting Without Deleting Pod")
    exit(3)


### Checking for Active Processes

check_processes = f"kubectl exec -i {pod_name} -- /bin/bash -c 'ps -a'"
running_processes = sp.run(check_processes, shell=True, capture_output=True
                          ).stdout.decode().split('\n')[1:]
running_processes = [x.strip() for x in running_processes if x.strip()]
if running_processes:
    print("Running Processes Found")
    print("Exiting Without Deleting Pod")
    exit(4)


### Checking for Active Tmux Sessions

check_tmux = f"kubectl exec -i {pod_name} -- /bin/bash -c 'tmux ls'"
tmux_sessions = sp.run(check_tmux, shell=True, capture_output=True
                          ).stdout.decode().strip().split('\n')

tmux_sessions = [x for x in tmux_sessions if not x.startswith('jupyter_nbk')]
if tmux_sessions:
    print("Tmux Session Found")
    print("Exiting Without Deleting Pod")
    exit(5)


### Closing Pod

deployment = '-'.join(pod_name.split('-')[:-2])
print(f"Closing Inactive Kubectl Deployment {deployment}")
sp.run(f"kubectl delete deployments {deployment}", shell=True)

