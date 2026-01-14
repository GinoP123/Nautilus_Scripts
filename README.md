# Nautilus Scripts

*General Nautilus Tutorials:*
https://nrp.ai/documentation/userdocs/start/getting-started/

*Logging in to a Pod*
```
./bin/kubectl_login.sh
```

*Creating a New Pod*
```
./bin/start_kubectl_pod.py
```

*Downloading Files*
```
./bin/download.sh <NAUTILUS_PATH> <LOCAL_PATH>
```

*Uploading Files*
```
./bin/upload.sh <LOCAL_PATH> <NAUTILUS_PATH>
```

*Listing Available Pods*
```
./bin/get_pod_list.sh
```

*Viewing Available Resources*
https://nrp.ai/viz/resources/

*Reservations for Nodes*
https://nrp.ai/reservations/

## Required Packages

```
pip install -r requirements.txt
```

### Mac

```
brew tap mklement0/ttab https://github.com/mklement0/ttab.git
brew install mklement0/ttab/ttab
```
