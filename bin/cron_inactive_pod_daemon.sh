#!/bin/bash

script_dir=$(dirname "$0")

pvc='bafnavol'

POD_NAME=$("$script_dir/get_current_pod.sh" $pvc)

if [[ $? != 0 ]]; then
	echo "No Pods Found"
	exit 1
fi

"$script_dir/close_inactive_pod.py" "$POD_NAME"

