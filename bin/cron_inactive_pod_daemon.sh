#!/bin/bash

script_dir=$(dirname "$0")
pvc_profiles=$("$script_dir/settings.py" pvc_profiles)
pvc_list=$(python3 -c "import ast; print(' '.join(ast.literal_eval(\"$pvc_profiles\")))")
day_of_week=$(date +%A)

for pvc in $pvc_list
do
	POD_NAME=$("$script_dir/get_current_pod.sh" $pvc)

	echo "PVC: $pvc"
	if [[ $? != 0 ]]; then
		echo "No Pods Found"
	fi

	if [[ "$day_of_week" =~ ^(Sunday|Wednesday|Friday)$ ]]; then
		"$script_dir/close_inactive_pod.py" "$POD_NAME"
	fi
done

date

