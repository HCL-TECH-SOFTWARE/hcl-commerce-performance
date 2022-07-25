# HCL Cache - Remote Cache Tuning Configurations

This document describes cache level tuning configurations for remote caches:

- [Compression](#Compression)
- [Sharding](#Sharding)
- [Inactivity](#Inactivity)
- [Optimizations for Clear Operations](#optimizations-for-cache-clear-operations)

See [Cache Configuration](CacheConfiguration.md) for details on how these settings can be applied to custom or out of the box caches.

## Compression

> Compression is available since 9.1.6. It is disabled by default.

The HCL Cache provides the option to use a compression algorithm [LZ4](https://github.com/lz4/lz4) on the cache key values. Compression is not enabled by default. Caches with large keys, such as JSP caching in baseCache can benefit from compression.
Compression reduces the size of the keys in Redis, and reduces network trafic, but it can increase CPU usage on the client containers. You might see no benefit from enabling compression on caches with small keys.

To enable compression, add `codec: compressing` under the `remoteCache` element for the desired cache.
```
cacheConfigs:
  baseCache:
    remoteCache:
      codec: compressing
```

## Sharding

> Sharding is available since 9.1.10. The number of shards defaults to 1.

To enable sharding, add the `shards` configuration under the `remoteCache` element for a particular cache, with a value higher than 1.

```
cacheConfigs:
  baseCache:
    remoteCache:
      shards: 3
```

When sharding is enabled, the cache is internally partitioned by the number of shards specified. For example, if 3 shards are specified, 3 shards are created. Regardless of the number of shards, invalidation processing is still handled at the cache level--each shard processes all invalidations for its cache. 

```
{cache-demoqalive-baseCache}-invalidation
{cache-demoqalive-baseCache:s=0}-(dep|data)
{cache-demoqalive-baseCache:s=1}-(dep|data)
{cache-demoqalive-baseCache:s=2}-(dep|data)
```

As each shard is assigned a unique hash slot, sharding is typically used with Redis Clustering, as it allows each shard or cache segment to be handled by a different Redis node.
Sharding can help for caches that might overwhelm a single Redis node, either due to their memory footprint, or the amount of load/operations they generate. `baseCache` is an example of a cache that might benefit from sharding.

> In a Redis cluster environment, the slot assignment is done considering the namespace, cache name and shard number. It's not guaranteed that the shards will be evenly distributed across the Redis nodes, but this can be overcome by increasing the number of shards or using [slot migration](https://redis.io/commands/cluster-setslot/).

### Impact of sharding on cache operations

Get | Put | Invalidate | Clear
--- | --- | --- | --- |
A hashing algorithm is applied over the *cache-id* to select the shard that the cache entry should be retrieved from. Sharding has negligible impact on "get" operations | A hashing algorithm is applied over the *cache-id* to select the shard that the cache entry will be assigned to. Sharding has negligible impact on "put" operations | Invalidations must be executed against all shards. This is done in parallel.  |  A clear operation must be executed against all shards. This is done in parallel. | 

### Parallel processing of invalidate and clear operations

The HCL Cache uses a thread pool to perform *invalidate* and *clear* shard operations in parallel.  The thread pool size is configured with the `numAsyncCacheOperationThreads` setting, which is configured at the top level of the YAML configuration:

```
numAsyncCacheOperationThreads: -1
cacheConfig:
  ... 
```

`numAsyncCacheOperationThreads` defaults to `-1`, which translates to the maximum number of shards configured for any cache. 

When an *invalidate* or *clear* operation is executed on a sharded cache, the HCL Cache attempts to use the threadpool to execute in parallel. If the thread pool has no queued threads, all shards will be executed concurrently. If the thread pool is in use, and there are queued tasks, the threadpool is not used and each shard is processed sequentially. This is to manage a potential case where multiple *invalidate* operations are executed concurrently on a sharded cache, which might require a large number of threads to be active. 

## Inactivity

> Inactivity is available since 9.1.10. It is disabled by default.

The configuration of inactivity enables the HCL Cache to track and evict entries that are not seeing reuse. By removing idle entries before their expiry time, the total cache memory used is reduced which makes the cache run more efficiently.

As tracking of inactive entries adds a processing cost, inactivity is not currently enabled by default. Instead, it is enabled for selected out of the box caches, and can be enabled for other out of the box or custom caches.

To enable removal of inactive cache entries, specify `enabled: true` and specify a number of minutes using the `inactivityMins` configuration.

```
cacheConfigs:
  baseCache:
    remoteCache:
      onlineInactiveEntriesMaintenance:
        enabled: true
        inactivityMins: 30
```

See [Cache Maintenance](HCLCacheMaintenance.md) for details on how inactivity maintenance is performed, and can be monitored and tuned.

### Use of inactivity with local caches
Local caches support inactivity at the cache entry level. Inactivity can be configured using the *cachespec.xml*, or programatically with the [DistributedMap](CustomCaching.md) interface. Inactivity set by DynaCache is used for local caching only and doesn't impact the inactivity process of the remote cache, which must be enabled independently.

### Inactivity vs Low Memory Maintenance
Production environments generate large amounts of cache. Certain caches, such as users or "searchTerm", can grow unbounded and eventually fill up the remote cache memory (*maxmemory*). When Redis memory usage is near the limit, Low Memory Maintenance triggers to maintain the  usage under 100%. 
The use of Inactivity Maintenance can eliminate or reduce the processing done for Low Memory Maintenance. The use of Inactivity Maintenance is more efficient as follows:
- Inactivity Maintenance runs continuously, while Low Memory Maintenance only triggers when the memory is nearly full. Keeping a smaller memory footprint allows Redis to run more efficiently, including high availability operations such as persistence and recovery.
- Inactivity Maintenance runs from all containers, while Low Memory Mainteance is active from only a single container at any one time.
- Low Memory Maintenance must remove a percentage of the cache, and it does so by selecting entries that are sooner to be expired, even if they may have high reuse. However, Inactivity Maintenance only removes inactive entries, helping to retain other high reuse entries.

### Inactivity and skip-remote cache directive
The HCL Cache has special configurations called [Cache directives](CacheDirectives.md) that are used with cache entries to skip local or remote caching.
Caches that enable local and remote caching, and deal with entries that might not see reuse, such as REST calls that specify searchTerm, faceting and pagination, may benefit from these configurations. Caches that create many cache entries that are not reused can be inefficient--disabling remote caching for those caches can help reduce remote cache memory footprint.
Since 9.1.10, you might choose to allow these entries in the remote cache, while relying on Inactivity processing to remove inactive entries.

#### QueryApp REST Caching for searchTerm 
The QueryApp container implements the *skip-remote* directive for certain "searchTerm" caches in cachespec.xml. If you enable Inactivity for baseCache, consider allowing these caches to use the remote cache, by customizing the cachespec.xml file to remove the following snippets:

``` 
<component id="DC_HclCacheSkipRemote" type="attribute">
  <required>true</required>
</component>
```

## Optimizations for Cache Clear Operations

Remote cache clear operations work by scanning the Redis database, and deleting all the keys that match the cache prefix (e.g. *"{cache-demoqalive-baseCache}-*"*.).
This algorithm is most efficient with large caches, or with caches that account for a large percentage of the total keys.

When clearing a small cache, the algorithm must still scan the whole the database for matching keys. As the cache clear operation is non-blocking, the scanning might be slow and require many calls to the Redis server.

For small caches, it is more efficient to use the *invalidate* logic. The *invalidate* logic processes each cache entry and its dependency ids, but avoids the complete database scan by using the [dependency id set](HCLCacheInRedis.md#dependency-id-information). To perform a clear, the invalidate logic is executed with the `&ALL&` implicit dependency id, which is associated to all the keys in the cache.

The HCL Cache is configured to use the invalidate algorithm for cache clears with the setting `smallCacheClearOptimizationMaximumSize`, which is enabled by default with a value of `50000`.

> smallCacheClearOptimizationMaximumSize is available since 9.1.6.

```
cacheConfigs:
  baseCache:
    remoteCache:
      smallCacheClearOptimizationMaximumSize: 50000
```

