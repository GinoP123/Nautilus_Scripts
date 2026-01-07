#!/bin/bash

script_dir=$(dirname "$0")

upload_path="$1"
destination_path="$2"

if [[ $upload_path == '' ]]; then
	echo -e "\n\tERROR: Missing Upload Directory\n"
	exit 1
elif [[ $destination_path == '' ]]; then
	echo -e "\n\tERROR Missing Destination Directory\n"
	exit 2
fi

bafnavol_regex='^/home/bafnavol/.*'
ecvol_regex='^/home/ecvol/.*'
if [[ "$destination_path" =~ $bafnavol_regex ]]; then
	POD_NAME=$("$script_dir/get_current_pod.sh" bafnavol)
elif [[ "$destination_path" =~ $ecvol_regex ]]; then
	POD_NAME=$("$script_dir/get_current_pod.sh" ecvol)
else
	echo "ERROR: Invalid Destination Path"
	exit 1
fi

basename_="$(basename "$upload_path")"
kubectl cp "$upload_path" "ecdna/$POD_NAME:work/"
kubectl exec -it $POD_NAME -- /bin/bash -c "mv '/home/jovyan/work/$basename_' '$destination_path'"

