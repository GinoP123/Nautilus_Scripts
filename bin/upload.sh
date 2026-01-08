#!/bin/bash

script_dir=$(dirname "$0")
namespace=$("$script_dir/settings.py" namespace)

upload_path="$1"
destination_path="$2"

if [[ $upload_path == '' ]]; then
	echo -e "\n\tERROR: Missing Upload Directory\n"
	exit 1
elif [[ $destination_path == '' ]]; then
	echo -e "\n\tERROR Missing Destination Directory\n"
	exit 2
fi


regex='s|^/home/\([^/]*\)/.*$|\1|p'
pwc=$(echo $destination_path | sed -n $regex)
POD_NAME=$("$script_dir/get_current_pod.sh" "$pwc")
if [[ $? != 0 || $pwc == "" ]]; then
	echo "ERROR: Invalid Destination Path"
	exit 1
fi

basename_="$(basename "$upload_path")"
kubectl cp "$upload_path" "$namespace/$POD_NAME:work/"
kubectl exec -it $POD_NAME -- /bin/bash -c "mv '/home/jovyan/work/$basename_' '$destination_path'"

