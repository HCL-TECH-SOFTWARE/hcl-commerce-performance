# Redis Servers for HCL Cache

## Redis server requirements for HCL Commerce

Although the use of a remote cache in Redis is highly recommended, it is not required in all configurations as follows:

**Elastic Search**: Redis is required. The Redis servers must be shared by authoring and live. This is required as NiFi must interact with both authoring and live environments. 

**Solr Search**: Redis is recommended but not required. Migrated environments that do not implement Redis must continue using Kafka to replicate invalidations. Redis replaces Kafka for invalidations and can also act as a remote cache. Authoring and Live can be configured with separate Redis servers. This is recommended for production environments.

## Selecting a Redis topology

Redis can be installed in a variety of configurations. The selection depends on your performance and high-availability requirements. 
The alternatives include:
- Using the [Bitnami Charts](BitnamiRedisInstall.md) to install Redis within the Kubernetes cluster
- Redis Enterprise by RedisLabs
- Redis as-a-service from a cloud provider

### Standalone and Cluster configurations

Redis standalone (single instance) will work appropriately for pre-production and many production environments. Larger environments can benefit from a clustered Redis, which allows for multiple masters and replicas. 

A Redis Cluster is configured with multiple masters (3+). Caches and [shards](RemoteCacheTuningConfigurations.md#Sharding) will be distributed across the master servers. Each master can be configured with zero or more replicas. Replicas can help scalability by handling read traffic (GET operations) and can take over should the master become unavailable. 

## Required configurations

Use the following configurations in the Redis server. See [key eviction](https://redis.io/docs/manual/eviction/) for details.

- *maxmemory*: indicates the amount of memory available to hold cached data, and should be set to a non-zero value.
- *maxmemory-policy*: must be set to *volatile-lru*

## Key Tuning configurations

Besides the topology, consider the following key tuning configurations. Most apply to locally installed Redis, but can be relevant to redis as-a-service as well.

To validate, or compare  the performance of the Redis server, you can use the The [Redis benchmark utility](https://redis.io/docs/reference/optimization/benchmarks/), and
the HCL Cache's [hcl-cache-benchmark](Utilities.md#hcl-cache-benchmark) utility. 

### Use fast CPUs and fast storage

Redis is mostly single-threaded, at least from the command execution point-of-view. It benefits from fast processors with high frequency rate. If persistence is enabled,
the containers will also benefit from fast storage. Use a premium storage class that is backed by SSDs. 

### Validate the Kubernetes limits

Ensure the limits set on the Redis pods are set appropiately:
- *Storage:* If persistence is used, the Persistent Volumes needs to be sized acordingly. For example, the [Bitnami Charts](BitnamiRedisInstall.md) set a limit of 8GB by default. This might not be enough for production environments and might lead to a crash.
 - *CPU:* CPU Throttling can freeze the Redis server. Kubernetes is very agressive with CPU throttling. To avoid it, set a high limit, or remove the CPU limit for the Redis pods. 
 - *Memory:* The memory required by the Redis container is a function of the *maxmemory* configuration. *maxmemory* should be less than 70% of the container limit
 
### Redis Persistence
 
Redis includes [persistence](https://redis.io/topics/persistence) (AOF/RDB) options that save the memory contents to disk. This allows Redis to recover the memory contents (cache) in case of a crash. For the use with HCL Cache, enabling RDB persistence and disabling AOF should be sufficient.

Persistence is required when replicas are used.  Otherwise, it is optional and Redis does not require a Persistence Volume. Without persistence, in the unlikely case that Redis crashes or becomes unresponsive, Kubernetes should be able to restart the service almost instantaneously, but with an empty cache.

If the Commerce site is not tuned to absorb a cache clear during  peak traffic period, persistence is recommended. When persistence is enabled, the startup will be delayed by a number of seconds while Redis re-loads the memory cache from disk. It is also possible that if the Kubernetes node crashes, manual intervention may be required to release the Persistence Volume from the problematic node and to allow Kubernetes to reschedule the pod (due to ReadWriteOnce-RWO mode).


*Disclaimer: Redis is a registered trademark of Redis Labs Ltd. Any rights therein are reserved to Redis Labs Ltd. Any use by HCL is for referential purposes only and does not indicate any sponsorship, endorsement, or affiliation between Redis Labs Ltd.*


