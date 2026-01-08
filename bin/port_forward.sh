#!/bin/bash


pod_name=$1
port=$2

ERROR=$(kubectl port-forward $pod_name $port:$port  2>&1 | grep 'lost connection' )
while [[ $ERROR != '' ]]
do
  ERROR=$(kubectl port-forward $pod_name $port:$port 2>&1 | grep 'lost connection' ); 
  sleep 5; 
done

