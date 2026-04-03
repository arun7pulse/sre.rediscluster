# Redis Cluster on Kubernetes

A comprehensive guide to deploying and managing a Redis cluster on Kubernetes. This repository demonstrates Redis cluster concepts and provides a complete setup for development and demonstration purposes.

## Overview

This project deploys a high-availability Redis cluster on Kubernetes using StatefulSets. The cluster consists of:
- 6 Redis pods (3 primary nodes + 3 replicas)
- Automatic slot distribution
- Pod anti-affinity for node distribution (optional)
- Persistent storage using PVCs
- Pod disruption budgets for high availability

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Redis Cluster Service                   │
│              (Headless ClusterIP Service)                │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼───┐        ┌───▼───┐        ┌───▼───┐
    │ Pod 0 │        │ Pod 1 │        │ Pod 2 │
    │Primary│        │Primary│        │Primary│
    │Slots: │        │Slots: │        │Slots: │
    │0-5460 │        │5461-  │        │10923- │
    │       │        │10922  │        │16383  │
    └───┬───┘        └───┬───┘        └───┬───┘
        │                │                │
    ┌───▼───┐        ┌───▼───┐        ┌───▼───┐
    │ Pod 3 │        │ Pod 4 │        │ Pod 5 │
    │Replica│        │Replica│        │Replica│
    └───────┘        └───────┘        └───────┘
```

## Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl configured to access your cluster
- jq (for JSON parsing in commands)
- At least 60Gi of available storage (10Gi per pod)

## Quick Start

### 1. Deploy the Redis Cluster

```bash
kubectl create -f redis-cluster.yaml
```

This will create:
- A headless service for cluster communication
- A ConfigMap with Redis cluster configuration
- A StatefulSet with 6 Redis pods
- PersistentVolumeClaims for each pod
- A PodDisruptionBudget

### 2. Wait for Pods to be Ready

```bash
kubectl get pods -l app=redis-cluster -w
```

Wait until all 6 pods are in the `Running` state with `1/1` ready.

### 3. Initialize the Cluster

Export the Redis node IPs and create the cluster:

```bash
# For default namespace
export REDIS_NODES=$(kubectl get pods -l app=redis-cluster -n default -o json | jq -r '.items | map(.status.podIP) | join(":6379 ")'):6379

# Initialize the cluster with 1 replica per primary
kubectl exec -it redis-cluster-0 -n default -- redis-cli --cluster create --cluster-replicas 1 ${REDIS_NODES}
```

Type `yes` when prompted to accept the cluster configuration.

### 4. Verify the Cluster

Check cluster status:

```bash
kubectl exec -it redis-cluster-0 -n default -- redis-cli cluster info
```

Check each node's role:

```bash
for x in $(seq 0 5); do
  echo "=== redis-cluster-$x ==="
  kubectl exec redis-cluster-$x -n default -- redis-cli role
  echo
done
```

## Testing the Cluster

### Using the Kubernetes Client

The `k8-redis-client.py` script connects to the cluster from within Kubernetes:

```bash
# Update the host IP in k8-redis-client.py to match one of your pod IPs
python3 k8-redis-client.py
```

### Using the Local Client

For local testing (requires port-forwarding):

```bash
# Forward port 6379 from one of the pods
kubectl port-forward redis-cluster-0 6379:6379

# In another terminal, run the local client
python3 local-redis-client.py
```

### Manual Testing

```bash
# Connect to a pod
kubectl exec -it redis-cluster-0 -n default -- redis-cli

# Test cluster operations
127.0.0.1:6379> CLUSTER INFO
127.0.0.1:6379> CLUSTER NODES
127.0.0.1:6379> SET mykey "Hello"
127.0.0.1:6379> GET mykey
```

## Configuration

### Adjusting Cluster Size

To change the number of shards (primary nodes), modify the `NUM_SHARDS` environment variable in `redis-cluster.yaml`:

```yaml
env:
  - name: NUM_SHARDS
    value: "3"  # Change this value
```

**Important**: Ensure `replicas` is at least 2x the number of shards.

### Storage Configuration

Modify the storage size in the `volumeClaimTemplates` section:

```yaml
volumeClaimTemplates:
  - metadata:
      name: datadir
    spec:
      resources:
        requests:
          storage: 10Gi  # Adjust as needed
```

## Files Description

- `redis-cluster.yaml` - Main deployment file with Service, ConfigMap, and StatefulSet
- `k8-redis-client.py` - Python client for testing from within Kubernetes
- `local-redis-client.py` - Python client for local testing
- `redis-expose.yaml` - Service configuration for external access
- `values.yaml` - Helm-style values (for reference)

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod redis-cluster-0
kubectl logs redis-cluster-0
```

### Cluster Not Forming

Check that the redis-cluster service is accessible:

```bash
kubectl get svc redis-cluster
kubectl describe svc redis-cluster
```

### Storage Issues

Check PVC status:

```bash
kubectl get pvc
```

### Reset the Cluster

```bash
kubectl delete -f redis-cluster.yaml
kubectl delete pvc -l app=redis-cluster
kubectl create -f redis-cluster.yaml
```

## Cleanup

```bash
kubectl delete -f redis-cluster.yaml
kubectl delete pvc -l app=redis-cluster
```

## Production Considerations

For production deployments, consider:

1. **Enable Pod Anti-Affinity**: Uncomment the `affinity` section in `redis-cluster.yaml` to ensure pods run on different nodes
2. **Resource Limits**: Add CPU and memory limits to the pod spec
3. **Monitoring**: Integrate with Prometheus/Grafana for metrics
4. **Backup Strategy**: Implement regular backups of AOF/RDB files
5. **Network Policies**: Restrict access to Redis ports
6. **TLS/Authentication**: Enable AUTH and TLS for secure communication

## References

- [Redis Cluster Specification](https://redis.io/topics/cluster-spec)
- [Redis on Kubernetes Best Practices](https://redis.io/topics/cluster-tutorial)
- [Kubernetes StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)

## License

MIT License - See LICENSE file for details.

## Contributing

Feel free to open issues or submit pull requests for improvements.