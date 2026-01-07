#!/bin/bash


pod_name=$1
port=$2
until kubectl port-forward "$pod_name" "$port:$port" 2>&1 | grep -q 'lost connection'; do
  echo "Port-forward crashed or finished. Restarting in 1s..."
  sleep 1
done


