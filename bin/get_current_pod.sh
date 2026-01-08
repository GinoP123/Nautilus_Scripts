#!/bin/bash


pvc="$1"
if [[ $pvc == "" ]]; then
	pvc='jovyan'
fi

PODS=$(kubectl get pods | awk 'NR>1{print $1}')

for pod in $PODS; do
	output=$(kubectl exec -i "$pod" -- /bin/bash -c "ls \$PWD/..")
	if [[ "$pod" != "" && $output =~ "$pvc" ]]; then
		echo "$pod"
		exit 0
	fi
done

exit 1
