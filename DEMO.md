# Redis Cluster Demo Guide

This guide walks you through a complete demonstration of the Redis cluster on Kubernetes, including deployment, testing, and common operations.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Deploying the Cluster](#deploying-the-cluster)
3. [Verifying the Deployment](#verifying-the-deployment)
4. [Testing with Python Clients](#testing-with-python-clients)
5. [Redis CLI Operations](#redis-cli-operations)
6. [Cluster Management](#cluster-management)
7. [Failover Testing](#failover-testing)
8. [Cleanup](#cleanup)

## Initial Setup

### Prerequisites Check

```bash
# Verify kubectl is installed and configured
kubectl version --client

# Verify you have access to a Kubernetes cluster
kubectl cluster-info

# Check available storage classes (for PVCs)
kubectl get storageclass

# Verify jq is installed (for JSON parsing)
jq --version
```

### Clone the Repository

```bash
git clone https://github.com/arun7pulse/sre.rediscluster.git
cd sre.rediscluster
```

## Deploying the Cluster

### Step 1: Review the Configuration

```bash
# View the Redis cluster configuration
cat redis-cluster.yaml
```

Key components:
- **Service**: Headless service for pod-to-pod communication
- **ConfigMap**: Redis cluster configuration
- **StatefulSet**: 6 Redis pods with persistent storage
- **PodDisruptionBudget**: Ensures high availability

### Step 2: Deploy to Kubernetes

```bash
# Create all resources
kubectl create -f redis-cluster.yaml

# Expected output:
# service/redis-cluster created
# poddisruptionbudget.policy/redis-cluster-pdb created
# configmap/redis-cluster-config created
# statefulset.apps/redis-cluster created
```

### Step 3: Monitor Pod Creation

```bash
# Watch pods being created
kubectl get pods -l app=redis-cluster -w

# Wait for all pods to show 1/1 READY
# This may take 2-5 minutes depending on your cluster
```

## Verifying the Deployment

### Check Pod Status

```bash
# List all Redis pods
kubectl get pods -l app=redis-cluster -o wide

# Example output:
# NAME              READY   STATUS    RESTARTS   AGE   IP
# redis-cluster-0   1/1     Running   0          2m    10.244.1.5
# redis-cluster-1   1/1     Running   0          2m    10.244.2.3
# redis-cluster-2   1/1     Running   0          1m    10.244.1.6
# redis-cluster-3   1/1     Running   0          1m    10.244.2.4
# redis-cluster-4   1/1     Running   0          1m    10.244.1.7
# redis-cluster-5   1/1     Running   0          1m    10.244.2.5
```

### Check Persistent Volumes

```bash
# View PVCs
kubectl get pvc

# View PVs
kubectl get pv
```

### Check Service

```bash
# View the Redis service
kubectl get svc redis-cluster

# Describe the service
kubectl describe svc redis-cluster
```

## Initializing the Cluster

### Step 1: Get Pod IPs

```bash
# Export Redis node IPs
export REDIS_NODES=$(kubectl get pods -l app=redis-cluster -n default -o json | jq -r '.items | map(.status.podIP) | join(":6379 ")'):6379

# Verify the variable
echo $REDIS_NODES
# Example output: 10.244.1.5:6379 10.244.2.3:6379 10.244.1.6:6379 10.244.2.4:6379 10.244.1.7:6379 10.244.2.5:6379
```

### Step 2: Create the Cluster

```bash
# Initialize the cluster with 1 replica per primary
kubectl exec -it redis-cluster-0 -n default -- redis-cli --cluster create --cluster-replicas 1 ${REDIS_NODES}

# You'll see output like:
# >>> Performing hash slots allocation on 6 nodes...
# Master[0] -> Slots 0 - 5460
# Master[1] -> Slots 5461 - 10922
# Master[2] -> Slots 10923 - 16383
# ...
# Can I set the above configuration? (type 'yes' to accept):
```

Type `yes` to accept the configuration.

### Step 3: Verify Cluster Creation

```bash
# Check cluster info
kubectl exec -it redis-cluster-0 -n default -- redis-cli cluster info

# Expected output should include:
# cluster_state:ok
# cluster_slots_assigned:16384
# cluster_known_nodes:6
```

## Testing with Python Clients

### Local Client (via Port-Forward)

```bash
# Terminal 1: Set up port forwarding
kubectl port-forward redis-cluster-0 6379:6379

# Terminal 2: Install dependencies and run client
pip install redis-py-cluster
python3 local-redis-client.py

# Expected output:
# Connecting to Redis cluster at localhost:6379...
# ✓ Connected successfully!
#
# Setting key 'demo:test' = 'Hello from local client!'
# Getting key 'demo:test'...
# ✓ Retrieved: Hello from local client!
# ...
```

### Kubernetes Client

```bash
# Create a test pod
kubectl run -it --rm redis-client --image=python:3.9 --restart=Never -- bash

# Inside the pod:
pip install redis-py-cluster
curl -O https://raw.githubusercontent.com/arun7pulse/sre.rediscluster/main/k8-redis-client.py
python3 k8-redis-client.py
```

## Redis CLI Operations

### Connect to a Pod

```bash
kubectl exec -it redis-cluster-0 -n default -- redis-cli
```

### Basic Commands

```bash
# Inside redis-cli:

# View cluster information
127.0.0.1:6379> CLUSTER INFO

# View all nodes
127.0.0.1:6379> CLUSTER NODES

# Set a key
127.0.0.1:6379> SET mykey "Hello Redis Cluster"
-> Redirected to slot [14687] located at 10.244.1.6:6379
OK

# Get a key
127.0.0.1:6379> GET mykey
"Hello Redis Cluster"

# Check which slot a key belongs to
127.0.0.1:6379> CLUSTER KEYSLOT mykey
(integer) 14687

# Get keys count (on current node)
127.0.0.1:6379> DBSIZE

# Exit
127.0.0.1:6379> EXIT
```

### Test Data Distribution

```bash
# Set keys that will be distributed across different slots
for i in {1..20}; do
  kubectl exec redis-cluster-0 -- redis-cli -c SET "key$i" "value$i"
done

# Check key distribution across nodes
for x in $(seq 0 5); do
  echo "=== redis-cluster-$x ==="
  kubectl exec redis-cluster-$x -- redis-cli DBSIZE
done
```

## Cluster Management

### Check Node Roles

```bash
# Check role of each node (primary/replica)
for x in $(seq 0 5); do
  echo "=== redis-cluster-$x ==="
  kubectl exec redis-cluster-$x -n default -- redis-cli role
  echo
done

# Example output:
# === redis-cluster-0 ===
# 1) "master"
# 2) (integer) 0
# 3) (empty array)
```

### Monitor Cluster Health

```bash
# Get cluster status from any node
kubectl exec redis-cluster-0 -- redis-cli --cluster check redis-cluster-0.redis-cluster.default.svc.cluster.local:6379
```

### View Logs

```bash
# View logs for a specific pod
kubectl logs redis-cluster-0

# Follow logs in real-time
kubectl logs -f redis-cluster-0

# View logs for all pods
kubectl logs -l app=redis-cluster --tail=50
```

## Failover Testing

### Simulate Node Failure

```bash
# Delete a primary node (e.g., redis-cluster-0)
kubectl delete pod redis-cluster-0

# Watch the cluster handle the failover
kubectl get pods -l app=redis-cluster -w

# Check that a replica was promoted to primary
kubectl exec redis-cluster-1 -- redis-cli cluster nodes
```

### Verify Data Persistence

```bash
# After the pod restarts, verify data is still accessible
kubectl exec -it redis-cluster-0 -- redis-cli -c GET mykey
```

### Test Rolling Updates

```bash
# Update Redis version in redis-cluster.yaml
# Then apply the change
kubectl apply -f redis-cluster.yaml

# Watch the rolling update
kubectl rollout status statefulset redis-cluster
```

## Advanced Operations

### Scaling the Cluster

```bash
# Scale to 9 pods (3 shards with 2 replicas each)
kubectl scale statefulset redis-cluster --replicas=9

# Wait for new pods
kubectl wait --for=condition=ready pod -l app=redis-cluster --timeout=300s

# Add new nodes to the cluster
# (Manual process - see Redis cluster documentation)
```

### Backup Data

```bash
# Trigger a BGSAVE on all nodes
for x in $(seq 0 5); do
  kubectl exec redis-cluster-$x -- redis-cli BGSAVE
done

# Check backup status
for x in $(seq 0 5); do
  echo "=== redis-cluster-$x ==="
  kubectl exec redis-cluster-$x -- redis-cli LASTSAVE
done
```

### Monitor Performance

```bash
# Get real-time stats
kubectl exec redis-cluster-0 -- redis-cli --stat

# Monitor specific commands
kubectl exec redis-cluster-0 -- redis-cli MONITOR

# Get slow log
kubectl exec redis-cluster-0 -- redis-cli SLOWLOG GET 10
```

## Cleanup

### Delete the Cluster

```bash
# Delete all resources
kubectl delete -f redis-cluster.yaml

# Delete PVCs (data will be lost!)
kubectl delete pvc -l app=redis-cluster

# Verify deletion
kubectl get pods -l app=redis-cluster
kubectl get pvc
```

### Troubleshooting Cleanup Issues

```bash
# If pods are stuck in Terminating state
kubectl delete pod redis-cluster-0 --grace-period=0 --force

# If PVCs are stuck
kubectl patch pvc datadir-redis-cluster-0 -p '{"metadata":{"finalizers":null}}'
```

## Common Issues and Solutions

### Issue: Pods Not Starting

**Solution:**
```bash
# Check pod events
kubectl describe pod redis-cluster-0

# Check if storage is available
kubectl get pvc
kubectl describe pvc datadir-redis-cluster-0
```

### Issue: Cluster Not Initializing

**Solution:**
```bash
# Ensure all pods are ready first
kubectl get pods -l app=redis-cluster

# Check redis-cli can connect
kubectl exec -it redis-cluster-0 -- redis-cli PING

# Verify service DNS
kubectl exec -it redis-cluster-0 -- nslookup redis-cluster
```

### Issue: Connection Refused

**Solution:**
```bash
# Check if Redis is listening
kubectl exec redis-cluster-0 -- netstat -tlnp | grep 6379

# Verify service endpoints
kubectl get endpoints redis-cluster
```

## Demo Script

Here's a complete script to run the entire demo:

```bash
#!/bin/bash
set -e

echo "=== Deploying Redis Cluster ==="
kubectl create -f redis-cluster.yaml

echo "=== Waiting for pods to be ready ==="
kubectl wait --for=condition=ready pod -l app=redis-cluster --timeout=300s

echo "=== Initializing cluster ==="
export REDIS_NODES=$(kubectl get pods -l app=redis-cluster -o json | jq -r '.items | map(.status.podIP) | join(":6379 ")'):6379
kubectl exec -it redis-cluster-0 -- redis-cli --cluster create --cluster-replicas 1 ${REDIS_NODES} --cluster-yes

echo "=== Verifying cluster ==="
kubectl exec redis-cluster-0 -- redis-cli cluster info

echo "=== Testing operations ==="
kubectl exec redis-cluster-0 -- redis-cli -c SET demo-key "Demo Complete"
kubectl exec redis-cluster-0 -- redis-cli -c GET demo-key

echo "=== Demo Complete! ==="
```

## Next Steps

- Explore the [README.md](README.md) for architecture details
- Review [redis-cluster.yaml](redis-cluster.yaml) for configuration options
- Try the Python clients for programmatic access
- Read about [Redis Cluster best practices](https://redis.io/topics/cluster-tutorial)
