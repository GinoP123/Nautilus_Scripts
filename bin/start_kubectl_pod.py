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
import glob
import io


### Loading Settings

port = settings.config['port']
pvc_profiles = settings.config['pvc_profiles']
pvc_list = list(pvc_profiles)


### Template Choice

script_dir = os.path.dirname(sys.argv[0])
pod_templates = glob.glob(f"{script_dir}/../pod_templates/*_template.yml")
choices = "\n\tPod Template\n"
for i, pod_template in enumerate(pod_templates, start=1):
    deployment_name = os.path.basename(pod_template)[:-len('_template.yml')]
    choices += f"\t\t{i}.): {deployment_name}\n"
print(choices)

choice = '0'
while not (choice.isnumeric() and (0 < int(choice) <= len(pod_templates))):
    choice = input("\tChoice: ")
template_path = pod_templates[int(choice)-1]

with open(template_path) as infile:
    new_pod = infile.read()


### Permanent Storage Choice

if 'VOLUME_NAME' in new_pod:
    choices = "\n\tPermanent Storage\n"
    for i, pvc in enumerate(pvc_list, start=1):
        choices += f"\t\t{i}.): {pvc}\n"
    print(choices)

    choice = '0'
    while not (choice.isnumeric() and (0 < int(choice) <= len(pvc_list))):
        choice = input("\tChoice: ")
    pvc = pvc_list[int(choice)-1]
    new_pod = new_pod.replace('VOLUME_NAME', pvc)
else:
    valid_pvc = False
    for pvc in pvc_list:
        if pvc in new_pod:
            valid_pvc = True
            break
    assert valid_pvc

profile = pvc_profiles[pvc]


### Checking if Permanent Volume Storage is already in use

returncode = sp.run(f"{script_dir}/get_current_pod.sh '{pvc}'", 
    capture_output=True, shell=True).returncode

if returncode != 1:
    print("\n\n\tERROR: Pod With Same Permanent Storage Already Exists\n")
    exit(1)


### Creating yaml file for pod

running_pods = sp.run("kubectl get pods", shell=True, 
    capture_output=True).stdout.decode().split('\n')[1:]
running_deployments = ['-'.join(x.split('-')[:-2]) for x in running_pods if x]

pod_outpath = f"{script_dir}/../pod_templates/deployment.yml"
deployment_name = yaml.safe_load(io.StringIO(new_pod))['metadata']['name']
deployment_name = deployment_name[:-len('_POD_NUM')]

next_deployment = 1
while f"{deployment_name}{next_deployment if next_deployment-1 else ''}" in running_deployments:
    next_deployment += 1
next_deployment = str(next_deployment) if next_deployment-1 else ''
new_pod = new_pod.replace('_POD_NUM', next_deployment)

with open(pod_outpath, 'w') as outfile:
    outfile.write(new_pod)


### Creating Pod

assert sp.run(f"kubectl create -f {pod_outpath}", shell=True).returncode == 0


### Waiting for Pod Startup

pod_name = ''
while not pod_name.strip():
    time.sleep(1)
    deployment_name = yaml.safe_load(io.StringIO(new_pod))['metadata']['name']
    pod_name = sp.run('kubectl get pods | grep "{}-" | cut -d" " -f1'.format(deployment_name), 
        shell=True, capture_output=True).stdout.decode().strip()

running = lambda: sp.run(f"kubectl get pods | grep {pod_name} | grep Running", 
    capture_output=True, shell=True).stdout.decode().strip() != ''
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
installation_commands = f'source {profile}; '
with open(installation_commands_path) as infile:
    installation_commands += '; '.join(infile.read().strip().split('\n'))

installation_commands = f"kubectl exec -i {pod_name} -- /bin/bash -c '{installation_commands}'"
assert sp.run(installation_commands, shell=True).returncode == 0


### Creating a new terminal

run_cmd_in_new_tab_script = f"{script_dir}/run_command_in_new_tab.sh"
new_login = f"'{run_cmd_in_new_tab_script}' kubectl exec -it {pod_name} -- /bin/bash"
sp.run(new_login, shell=True)
time.sleep(5)
port_forward_path = f"{script_dir}/port_forward.sh"
port_forward_job = sp.Popen(f"{port_forward_path} {pod_name} {port}", 
    shell=True, preexec_fn=os.setsid)


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
    response = requests.post(f'http://localhost:{port}/api/terminals', 
        cookies=get_response.cookies, data={'_xsrf': xsrf_value})

os.killpg(os.getpgid(port_forward_job.pid), signal.SIGTERM)

