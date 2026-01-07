#!/bin/bash

script_dir=$(dirname "$0")

download_path="$1"
destination_path="$2"

if [[ $download_path == '' ]]; then
	echo -e "\n\tERROR: No download path specified\n"
	exit 1
elif [[ "$destination_path" == '' || ! -d "$destination_path" ]]; then
	destination_path='.'
fi


bafnavol_regex='^/home/bafnavol/.*'
ecvol_regex='^/home/ecvol/.*'
if [[ "$download_path" =~ $bafnavol_regex ]]; then
	POD_NAME=$("$script_dir/get_current_pod.sh" bafnavol)
elif [[ "$download_path" =~ $ecvol_regex ]]; then
	POD_NAME=$("$script_dir/get_current_pod.sh" ecvol)
else
	echo "ERROR: Invalid Download Path"
	exit 1
fi

kubectl exec -i $POD_NAME -- /bin/bash -c "cp -r '$download_path' /home/jovyan/work"
kubectl cp --retries=10 "ecdna/$POD_NAME:work" "$destination_path"
kubectl exec -i $POD_NAME -- /bin/bash -c "rm -r '/home/jovyan/work/$(basename $download_path)'"


