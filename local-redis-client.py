#!/usr/bin/env python3
"""
Local Redis Cluster Client
===========================
This script demonstrates connecting to a Redis cluster from a local machine.
It requires port-forwarding from a Kubernetes Redis cluster pod.

Prerequisites:
    - pip install redis-py-cluster
    - kubectl port-forward redis-cluster-0 6379:6379

Usage:
    python3 local-redis-client.py
"""

from rediscluster import RedisCluster
from redis.exceptions import RedisClusterException, ConnectionError
import sys


def main():
    """Connect to Redis cluster and perform basic operations."""

    # Configuration
    # When using port-forward, the cluster will be accessible at localhost:6379
    startup_nodes = [{"host": "127.0.0.1", "port": "6379"}]

    try:
        # Initialize Redis cluster connection
        # decode_responses=True automatically decodes byte responses to strings (required for Python 3)
        print("Connecting to Redis cluster at localhost:6379...")
        rc = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True  # Allow connection even if not all slots are covered
        )

        # Test connection
        print("✓ Connected successfully!")

        # Perform test operations
        test_key = "demo:test"
        test_value = "Hello from local client!"

        print(f"\nSetting key '{test_key}' = '{test_value}'")
        rc.set(test_key, test_value)

        print(f"Getting key '{test_key}'...")
        result = rc.get(test_key)
        print(f"✓ Retrieved: {result}")

        # Get cluster info
        print("\nCluster Information:")
        print(f"Cluster size: {len(rc.cluster_nodes())} nodes")

        print("\n✓ All operations completed successfully!")

    except ConnectionError as e:
        print(f"✗ Connection Error: {e}", file=sys.stderr)
        print("\nMake sure you have port-forwarding enabled:", file=sys.stderr)
        print("  kubectl port-forward redis-cluster-0 6379:6379", file=sys.stderr)
        sys.exit(1)

    except RedisClusterException as e:
        print(f"✗ Redis Cluster Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()