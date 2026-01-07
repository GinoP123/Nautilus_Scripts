#!/bin/bash

PODS=$(kubectl get pods | awk 'NR>1{print $1}')

for pod in $PODS; do
	if [[ "$pod" != "" ]]; then
		echo "$pod"
	fi
done

# echo $(kubectl get pods | awk 'NR>1{print $1}')

