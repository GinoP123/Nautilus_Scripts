# Usage manual for 'ecdna' GPU cluster

**PI: Vineet Bafna**

**Admin: Utkrisht Rajkumar**

## Getting access to cluster

* To get access, email Utkrisht at urajkuma@eng.ucsd.edu. 
* Follow the instructions on this [page](http://ucsd-prp.gitlab.io/userdocs/start/quickstart/).

## Setting up a deployment and volume mount

* Create a `.yaml` to make a persistent volume claim (pvc). Save all your work on this pvc so that when you delete your pods, your data isn't lost. Any pod you create can be linked to this pvc to access the data. An example `pvc.yaml` file is pasted below. 

  ```yaml
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: ecvol
  spec:
    storageClassName: rook-block
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 100Gi
  ```

  `kubectl create -f pvc.yaml`

* Create `.yaml` file with the settings you want for the deployment. An example `dep.yaml` is pasted below. It comes pre-installed with most deep learning libraries, jupyter, etc.

  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dl
    namespace: ecdna
  spec:
    replicas: 1
    selector:
      matchLabels:
        k8s-app: ecpod
    template:
      metadata:
        labels:
          k8s-app: ecpod
      spec:
        affinity:
          nodeAffinity:
            requiredDuringSchedulingIgnoredDuringExecution:
              nodeSelectorTerms:
              - matchExpressions:
                - key: topology.kubernetes.io/region
                  operator: In
                  values:
                  - us-west
        containers:
        - name: ecdna
          image: [REPLACE WITH THE NEEDED IMAGE]
          command: ["sleep", "infinity"]
          resources:
            limits:
              cpu: 1
              nvidia.com/gpu: 8
              memory: "80Gi"
            requests:
              memory: "80Gi"
              cpu: 50m
          volumeMounts:
          - mountPath: /home/bafnavol
            name: bafnavol
          securityContext:
            runAsUser: 0  
        restartPolicy: Always
        volumes:
          - name: bafnavol
            persistentVolumeClaim:
              claimName: bafnavol
              readOnly: false
        nodeSelector:
          kubernetes.io/hostname: k8s-bafna-01.calit2.optiputer.net
        tolerations:
        - key: "nautilus.io/bafna"
          operator: "Equal"
          value: "true"
          effect: "NoSchedule"
  ```

  ​		Run: `kubectl create -f dep.yaml`	

* Then run `kubectl get pods`

* There should be a new pod that has started with the name `dl-<hash>`

* If the pod isn't properly starting, you can diagnose it using: `kubectl describe deployments <pod_name>`

  **Note:** You will need to toggle the memory limits based on the number of GPUs.  If using only 1 GPU, then 8-12Gi is plenty.

## Starting a pod or deleting a deployment

* `kubectl exec -it dl-<hash> bash`
* `kubectl delete deployments dl`

## Deploying jupyter notebook

To run jupyter, since the cluster doesn't have a GUI desktop, you will need to port forward the jupyter notebook to your local machine

* From local machine: ` kubectl port-forward pod_name to local_port:remote_port`

  Ex: `kubectl port-forward pod_name 8889:8888`

* From remote machine: `jupyter notebook --no-browser --port=8888 --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password=''`

* On a browser go to: https://localhost:8889

## Kill jupyter notebook instances

* To kill specific instance: `jupyter notebook stop <port-number> `
* To kill all instances: `pkill -f -1 jupyter*`


## Python environemnt

   
```
#Run just the below commands
sudo apt-get update
sudo apt-get install vim
conda env create -f env.yml

git config --global user.email urajkuma@eng.ucsd.edu
git config --global user.name "ucrajkumar"

jupyter notebook --no-browser --port=8888 --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password=''

jupyter notebook --no-browser --port=8888 --allow-root --ip='*' --NotebookApp.token='' --NotebookApp.password=''



For gpu pod, use tensorflow-gpu 2.4: https://www.tensorflow.org/install/source#gpu

```



