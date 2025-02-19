from rediscluster import RedisCluster

startup_nodes = [{"host": "10.43.191.202", "port": "6379"}]

rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

rc.set("foo", "bar")

print(rc.get("foo"))