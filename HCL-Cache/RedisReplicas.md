# Use of Redis Replicas

With Redis Cluster, master nodes can be backed by replicas (one or many), which are used for failover and scalability:

> Although other topologies support the use of replicas, this document is written with cluster in mind. You might sometimes see the terms *slave* and *replica* used interchangably. Note that with the standard [Bitnami Helm chart](https://github.com/bitnami/charts/tree/master/bitnami/redis) without sentinel, there is a single master and the replicas are never promoted to masters. Failover is provided by the use of Kubernetes probes to restart the master node.

On a Redis cluster install without replicas, Kubernetes probes are used to detect and restart unresponsive master nodes (pods in Kubernetes terminology). The master node is unavailable until its restart process is complete, or if [persistence](BitnamiRedisInstall.md#persistence) is enabled, until the persisted data (RDB/AOF) is finished loading to memory. The restart process can take a couple of minutes depending on the size of the memory dump and the hardware configuration.

Replicas are used to reduce downtime. They rely on the [replication](https://redis.io/docs/manual/replication/) process to mirror master node updates as they occur. If the Redis cluster detects a master node is down, it initiates failover to one of the master's replicas. The replica is then assigned the master role. When the master node that had crashed  recovers and joins the cluster, it recognizes that a new master is in place and configures itself as a replica.

## Using replicas for scalability

Besides their role for failover, replicas can increase scalability by handling read (Get) operations. This frees the master nodes and enables a more efficient use of resources.
When replicas are used for read operations, the following consideration must be made:

If a read operation happens immediately after a write, and before the change has been replicated, the read from the replica might return stale, or no data. This could introduce functional issues for certain caches or customizations scenarios (see [syncReplicas](#hcl-cache-configurations)).

When replicas are used for reads, both master and replica nodes must be available for optimal performance. Even though the Redis client uses the master node for reads if there are no replicas available, depending on the tuning and load levels, the master node alone might not have sufficient capacity to handle the combined read/write load (see [remote cache tuning](RemoteCacheTuningConfigurations.md)). Unavailable replicas can also lead to WAIT command timeouts, and failed read operations.

During failover, the Redis cluster promotes the replica to master. In the meantime, the Kubernetes probes are likely to restart the failed master which will return to the cluster a replica. The new replica attempts to replicate from the newly appointed master. Partial replication might fail requiring a full synchronization which can make the replica unavailable while the memory cache is loaded.

Although the Redis client falls back to the master node for reads if it detects the replicas are down (see [pingConnectionInterval](#redis-client-configurations)), this operation can slow down failover compared to when replicas are used exclusively for failover.

## Configurations

This section lists configurations relevant to the use of replicas for the Redis cluster, the Redis Client and the HCL Cache.

### Redis configurations

It is important to test replication and failover with load to verify that Redis will behave correctly during a production failover scenario. For example, the setting *cluster-replica-validity-factor*  could prevent the replica node from initiating failover and becoming a new master. A small *client-output-buffer-limit* value could lead to an endless replication loop, where full-replication fails and must be continuously restarted by the replica. The full-replication process might require peaks of memory usage, potentially exposing it to *OOMKilled* situation if the used memory exceeds the limit at any time.

The following are selected configurations for replication. See [redis.conf](https://raw.githubusercontent.com/redis/redis/6.2/redis.conf) for details.

- *repl-diskless-sync*: The Redis master creates a new process that directly writes the RDB file to replica sockets, without touching the disk at all. This is the default in Redis 7.
- *cluster-replica-validity-factor*: A replica of a failing master will avoid to start a failover if its data looks too old.  For maximum availability, set the cluster-replica-validity-factor to a value of 0, which means, that replicas will always try to failover the master regardless of the last time they interacted with the master.
- *client-output-buffer-limit*: A replica might be disconnected if the buffer is full due to the replica not reading data fast enough. 

Review the Redis container CPU and memory limits. The container memory limit must be set considering the `maxmemory` parameter. The limit is typically set so `maxmemory` is 50-70% of the total container limit. Memory usage can peak during failover operations, and if it exceeds the limit, the container could be *OOMKilled*.


### Redis Client configurations

The HCL Cache can be configured to issue read (GET) operations to replica servers with the [readMode](RedisClientConfig.md#read-mode) setting.
The [pingConnectionInterval](https://github.com/redisson/redisson/wiki/2.-Configuration/#pingconnectioninterval) (which defaults to 30 seconds), can be reduced to allow the Redis client to more quickly recognize an unavailable master or replica.

### HCL Cache configurations

The HCL Cache provides fine grained cache-level configurations that control if reads should be executed against replica or master nodes, and the use of the [WAIT](https://redis.io/commands/wait/) command. Although it should generally not be required, these configurations can be updated in the [cache configuration](CacheConfiguration.md).

The default configurations are as follows:

#### Commerce 9.1.11 default configuration

```
cacheConfigs:
  defaultCacheConfig:
    remoteConfig:
      syncReplicas: all:50
      limitSyncReplicasToNumberAvailable: true
      ignoreSyncReplicasWhenReadFromMaster: true
      forceReadFromMaster: false
```

#### Commerce 9.1.10 default configuration

```
cacheConfigs:
  defaultCacheConfig:
    remoteConfig:
      syncReplicas: ''
      limitSyncReplicasToNumberAvailable: true
      forceReadFromMaster: false
```

- `syncReplicas`: If enabled, the HCL Cache invokes the [WAIT](https://redis.io/commands/wait/) command after a `PUT` operation. The `WAIT` command introduces a delay until the configured number of replicas have processed the change, or the timeout is reached. Instead of specifiying a fixed number of replicas, it is possible to use `all` which translates to the number of replicas currently known by the Redis client. In 9.1.111+, Use `none` to disable.
*Example:* With the following configuration, the HCL Cache will wait until the change is replicated to all the available replicas, but will not wait more than the specified 250 milliseconds:
```
  syncReplicas: all:250
```
- `limitSyncReplicasToNumberAvailable`: When `syncReplicas` is enabled with a number of replicas, the `limitSyncReplicasToNumberAvailable` configuration can be used to restrict the configured number to the number of replicas currently known by the Redis client.
- `forceReadFromMaster`: When `readMode` is set to `SLAVE` or  `MASTER_SLAVE`, the `forceReadFromMaster` configuration ensures that reads (GETs) for this cache are sent to the master server. 
- `ignoreSyncReplicasWhenReadFromMaster`: The [WAIT](https://redis.io/commands/wait/) command helps maintain replicas in a consistent state. Although it plays a role for failover, it is more relevant when replicas are used for read operations as it can help ensure no stale data is served from the replica servers. As `syncReplicas` is enabled by default, this setting disables it when replicas are not used for reads. To ensure the WAIT command is issued regardless, configure this setting to false.

