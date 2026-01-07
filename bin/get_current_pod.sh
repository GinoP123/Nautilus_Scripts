#!/bin/bash


pwc="$1"
if [[ $pwc == "" ]]; then
	pwc='jovyan'
fi

PODS=$(kubectl get pods | awk 'NR>1{print $1}')

for pod in $PODS; do
	output=$(kubectl exec -i "$pod" -- /bin/bash -c "ls \$PWD/..")
	if [[ "$pod" != "" && $output =~ "$pwc" ]]; then
		echo "$pod"
		exit 0
	fi
done

exit 1
