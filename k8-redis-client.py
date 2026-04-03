#!/usr/bin/env python3
"""
Kubernetes Redis Cluster Client
================================
This script demonstrates connecting to a Redis cluster from within Kubernetes.
It should be run from a pod in the same cluster as the Redis pods.

Prerequisites:
    - pip install redis-py-cluster
    - Access to redis-cluster service in Kubernetes

Usage:
    1. Update the host IP to match one of your Redis pod IPs:
       kubectl get pods -l app=redis-cluster -o wide

    2. Run from within a Kubernetes pod:
       kubectl run -it --rm redis-client --image=python:3.9 -- bash
       pip install redis-py-cluster
       python3 k8-redis-client.py
"""

from rediscluster import RedisCluster
from redis.exceptions import RedisClusterException, ConnectionError
import sys
import os


def main():
    """Connect to Redis cluster from within Kubernetes."""

    # Configuration
    # Update this IP to match one of your Redis pod IPs
    # Get pod IPs with: kubectl get pods -l app=redis-cluster -o wide
    redis_host = os.getenv("REDIS_HOST", "redis-cluster-0.redis-cluster.default.svc.cluster.local")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    startup_nodes = [{"host": redis_host, "port": redis_port}]

    try:
        # Initialize Redis cluster connection
        print(f"Connecting to Redis cluster at {redis_host}:{redis_port}...")
        rc = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,  # Automatically decode byte responses to strings
            skip_full_coverage_check=False  # Ensure full cluster coverage
        )

        # Test connection
        print("✓ Connected successfully!")

        # Perform test operations
        test_key = "k8s:demo"
        test_value = "Hello from Kubernetes!"

        print(f"\nSetting key '{test_key}' = '{test_value}'")
        rc.set(test_key, test_value)

        print(f"Getting key '{test_key}'...")
        result = rc.get(test_key)
        print(f"✓ Retrieved: {result}")

        # Test multiple keys to show distribution across cluster
        print("\nTesting key distribution across cluster:")
        for i in range(5):
            key = f"k8s:test:{i}"
            value = f"value-{i}"
            rc.set(key, value)
            print(f"  Set {key} = {value}")

        # Get cluster info
        print("\nCluster Information:")
        nodes = rc.cluster_nodes()
        print(f"Cluster size: {len(nodes)} nodes")
        for node_name, node_info in nodes.items():
            print(f"  - {node_name}: {node_info}")

        print("\n✓ All operations completed successfully!")

    except ConnectionError as e:
        print(f"✗ Connection Error: {e}", file=sys.stderr)
        print(f"\nMake sure the Redis cluster is accessible at {redis_host}:{redis_port}", file=sys.stderr)
        print("Check pod IPs with: kubectl get pods -l app=redis-cluster -o wide", file=sys.stderr)
        sys.exit(1)

    except RedisClusterException as e:
        print(f"✗ Redis Cluster Error: {e}", file=sys.stderr)
        print("\nMake sure the cluster is initialized:", file=sys.stderr)
        print("  kubectl exec -it redis-cluster-0 -- redis-cli cluster info", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()