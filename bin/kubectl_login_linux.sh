#!/bin/bash

script_dir=$(dirname "$0")
IMPORT_JUPYTER=8888
EXPORT_JUPYTER=8888
"$script_dir/get_current_pod.sh" > /dev/null

PODS=$("$script_dir/get_my_pod_list.sh")
for pod in $PODS; do
	if [[ "$pod" != "" ]]; then
		pod_number=$((pod_number + 1))
		echo -e "\t\t$pod_number.): $pod"
	fi
done
echo -e "\t\t$((pod_number+1)).): Create a New Pod"

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
	yml_path="$script_dir/../pod_templates/gpu.yml"
	command="import re; print(re.search('(?<=name: ).*', open($yml_path).read()).group(0))"
	deployment_name=$(python3 -c "$command")
	POD_NAME=$(kubectl get pods | grep "$deployment_name-" | cut -d" " -f1)
else
	POD_NAME=$(echo $PODS | cut -d" " -f"${choice}")
fi

gnome-terminal -- bash -c "$script_dir/port_forward.sh $POD_NAME $EXPORT_JUPYTER"

wget http://localhost:$IMPORT_JUPYTER/tree -O /dev/null > /dev/null 2> /dev/null
while [[ $? != 0 ]]
do
    sleep 0.1
    wget http://localhost:$IMPORT_JUPYTER/tree -O /dev/null > /dev/null 2> /dev/null
done
open http://localhost:$IMPORT_JUPYTER/terminals/1

kubectl exec -it $POD_NAME -- /bin/bash

