#


## Install Statefulset and service 
```
kubectl create -f redis-cluster.yaml
```
## Start the clustr
```
export REDIS_NODES=$(kubectl get pods  -l app=redis-cluster -n redis -o json | jq -r '.items | map(.status.podIP) | join(":6379 ")'):6379
export REDIS_NODES=$(kubectl get pods  -l app=redis-cluster -n default -o json | jq -r '.items | map(.status.podIP) | join(":6379 ")'):6379
```
## Connect to client. 
```
kubectl exec -it redis-cluster-0 -n redis -- redis-cli --cluster create --cluster-replicas 1 ${REDIS_NODES}
kubectl exec -it redis-cluster-0 -n default -- redis-cli --cluster create --cluster-replicas 1 ${REDIS_NODES}
```


## Check the cluster details. 

```
for x in $(seq 0 5); do echo "redis-cluster-$x"; kubectl exec redis-cluster-$x -n default -- redis-cli role; echo; done
```
# sre.rediscluster
