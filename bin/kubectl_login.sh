#!/bin/bash

script_dir=$(dirname "$0")
port=$("$script_dir/settings.py" port)
"$script_dir/get_current_pod.sh" > /dev/null


### Listing Pod Choices

PODS=$("$script_dir/get_pod_list.sh")
for pod in $PODS; do
	if [[ "$pod" != "" ]]; then
		pod_number=$((pod_number + 1))
		echo -e "\t\t$pod_number.): $pod"
	fi
done
echo -e "\t\t$((pod_number+1)).): Create a New Pod"


### Selecting Pod

re="^[1-$((pod_number+1))]+\$"
echo -ne "\n\tChoice: "
read choice
while ! [[ $choice =~ $re ]]
do
	echo -ne "\tChoice: "
	read choice
done

if [[ $choice == $((pod_number+1)) ]]; then
	"$script_dir/start_kubectl_pod.py"
	yml_path="$script_dir/../pod_templates/deployment.yml"
	command="import yaml; print(yaml.safe_load(open('$yml_path'))['metadata']['name'])"
	deployment_name=$(python3 -c "$command")
	POD_NAME=$(kubectl get pods | grep "$deployment_name-" | cut -d" " -f1)
else
	POD_NAME=$(echo $PODS | cut -d" " -f"${choice}")
fi


### Killing Idle Port Forwarding Sessions

if [[ $(ps | grep "kubectl " | grep -v "grep" | awk '{print $1}' | wc -l) -ge 1 ]]; then
	while read -r id; do
		echo "Killing ID: $id"
		kill "$id"
	done < <(ps | grep "kubectl " | grep -v "grep" | awk '{print $1}')
fi
"$script_dir/run_command_in_new_tab.sh" "$script_dir/port_forward.sh" $POD_NAME $port


### Waiting For Jupyter Notebook Connection

wget http://localhost:$port/tree -O /dev/null > /dev/null 2> /dev/null
while [[ $? != 0 ]]
do
    sleep 0.1
    wget http://localhost:$port/tree -O /dev/null > /dev/null 2> /dev/null
done
open http://localhost:$port/terminals/1


### Opening Nautilus Terminal

kubectl exec -it $POD_NAME -- /bin/bash

