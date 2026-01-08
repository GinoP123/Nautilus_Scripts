#!/usr/bin/env python3

import subprocess as sp
import time
import requests
import os
import re
import signal
from datetime import datetime
import yaml
import sys
import settings

### Permanent Storage Choice

choices = "\n\tPermanent Storage\n"
for i, pvc in enumerate(settings.pvc_list, start=1):
    choices += f"\t\t{i}.): {pvc}\n"
print(choices)

choice = '0'
while not (choice.isnumeric() and (0 < int(choice) <= len(settings.pvc_list))):
    choice = input("\tChoice: ")
pvc = settings.pvc_list[int(choice)-1]

if pvc == 'bafnavol':
    profile = f"/home/{pvc}/{settings.username}/.profile"
else:
    profile = f"/home/{pvc}/.profile"


### Checking if Permanent Volume Storage is already in use

script_dir = os.path.dirname(sys.argv[0])
returncode = sp.run(f"{script_dir}/get_current_pod.sh '{pvc}'", 
    capture_output=True, shell=True).returncode

if returncode != 1:
    print("\n\n\tERROR: Pod With Same Permanent Storage Already Exists\n")
    exit(1)

### Creating yaml file for pod

running_pods = sp.run("kubectl get pods", shell=True, capture_output=True).stdout.decode().split('\n')[1:]
running_deployments = ['-'.join(x.split('-')[:-2]) for x in running_pods if x]

pod_outpath = f"{script_dir}/../pod_templates/gpu.yml"
template_path = f"{script_dir}/../pod_templates/template_pod.yml"

next_deployment = 1
while f"dl{next_deployment if next_deployment-1 else ''}" in running_deployments:
    next_deployment += 1
next_deployment = str(next_deployment) if next_deployment-1 else ''


with open(template_path) as infile:
    with open(pod_outpath, 'w') as outfile:
        new_pod = infile.read()
        new_pod = new_pod.replace('_POD_NUM', next_deployment)
        new_pod = new_pod.replace('VOLUME_NAME', pvc)
        outfile.write(new_pod)


### Creating Pod

assert sp.run(f"kubectl create -f {pod_outpath}", shell=True).returncode == 0


### Waiting for Pod Startup

pod_name = ''
while not pod_name.strip():
    time.sleep(1)
    with open("/Users/ginoprasad/Scripts/kubectl/bin/pod_templates/gpu.yml") as infile:
        deployment_name = re.search("(?<=name: ).*", infile.read()).group(0)
        pod_name = sp.run('/usr/local/bin/kubectl get pods | grep "{}-" | cut -d" " -f1'.format(deployment_name), shell=True, capture_output=True).stdout.decode().strip()

running = lambda: sp.run(f"/usr/local/bin/kubectl get pods | grep {pod_name} | grep Running", capture_output=True, shell=True).stdout.decode().strip() != ''
delta_t, start_time = 1, datetime.now()
while not running():
    print(f'Waiting for Pod Startup, Elapsed Time: {str(datetime.now() - start_time)}')
    time.sleep(delta_t)
    delta_t *= 1.5


### Updating bashrc

bashrc_update = f"echo 'source {profile}' >> /home/jovyan/.bashrc"
command = f"kubectl exec -i {pod_name} -- /bin/bash -c \"{bashrc_update}\""
assert sp.run(command, shell=True).returncode == 0


### Installing Packages

installation_commands_path = f"{script_dir}/../pod_templates/package_installations.txt"
installation_commands = f'source {profile};'
with open(installation_commands_path) as infile:
    installation_commands += '; '.join(infile.strip().split('\n'))
installation_commands = f"kubectl exec -i {pod_name} -- /bin/bash -c '{installation_commands}'"
assert sp.run(installation_commands, shell=True).returncode == 0


### Creating a new terminal

sp.run(f"{settings.terminal_open_script} kubectl exec -it {pod_name} -- /bin/bash", shell=True)
port_forward_path = f"{script_dir}/port_forward.sh"
port_forward_job = sp.Popen(f"{port_forward_path} {pod_name} {port}", shell=True, preexec_fn=os.setsid)


### Waiting for Port Forwarding Connection

valid_connection = False
delta_t, start_time = 1, datetime.now()
while not valid_connection:
    try:
        requests.get(f'http://localhost:{port}')
        valid_connection = True
    except requests.exceptions.ConnectionError:
        print(f'Waiting for Port Forwarding Connection, Elapsed Time: {str(datetime.now() - start_time)}')
        time.sleep(delta_t)
        delta_t *= 1.5


### Waiting for Jupyter Connection

terminals = eval(requests.get(f'http://localhost:{port}/api/terminals').text)
if not terminals:
    get_response = requests.get(f'http://localhost:{port}')
    xsrf_value = next(iter(get_response.cookies._cookies.values()))['/']['_xsrf'].value
    response = requests.post(f'http://localhost:{port}/api/terminals', cookies=get_response.cookies, data={'_xsrf': xsrf_value})

os.killpg(os.getpgid(port_forward_job.pid), signal.SIGTERM)

