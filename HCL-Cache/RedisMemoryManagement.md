# Memory Management in Redis
Redis is the database of choice to back cache systems. It's memory management model supports LRU (least recently used) and other algorithms to [evict](https://redis.io/docs/manual/eviction/) keys in order to allow for new data as the memory is full.

The HCL Cache has requirements that go beyond a simple key-value database. To support these requirements, such as invalidation by dependency, the cache must maintain sets of metadata for each key. Redis must not be allowed to evict metadata information, as this creates inconsistencies in the cache, such as entries not getting invalidated.
To maintain metadata, the HCL Cache implements a set of maintenance processes

## Redis memory configurations
The following configurations must be in place for Redis to be used with the HCL Cache:

- *maxmemory*: amount of memory made available for keys (cached data)
- *maxmemory-policy*: must be set to **volatile-lru**, which removes least recently used keys with the expire field set to true.

> With Redis Enterprise, maxmemory is not used. Caches are maintained using number of entries instead. See [softMaxSize](HCLCacheMaintenance.md).

## HCL Cache objects in Redis

Object | Use | Expiry Set
--- | --- | ---
**{}-data-*** | HASH key that contains the cached data and additional metadata, such as creation time, dependencies and others         |  YES
**{}-dep-***  | SET key for each dependency id. The set contains a list of all the cache id that are associated to this dependency id. |  NO
**{}-maintenance**  | ZSET by expiry time that contains cache keys and their dependencies |  NO
**{}-inactive**  | ZSET by creation time used for inactivity maintenance (9.1.10+) |  NO

Cached data (`{}-data-`) must always have an expiry set and may be evicted by Redis when available memory is exhausted. Metadata information (`{}-dep-,-maintenance,-inactive`) has no expiry and thus cannot be evicted by Redis. It must be maintained by HCL Cache maintenance processes.

## HCL Cache maintenance processes
In order to deal with metadata, the HCL Cache implements the following maintenance processes. For more details see: [Cache Maintenance](HCLCacheMaintenance.md).

### Expired Maintenance
When a key expires, Redis automatically removes it from memory. The Expired Maintenance job is responsible for removing references from the metadata to the expired key.

### Low-Memory Maintenance
When used memory reaches 100% of maxmemory, Redis starts evicting keys. Testing has shown that full memory conditions can lead to errors such as *"command not allowed when used memory > 'maxmemory'"*. To prevent this situation, the HCL Cache monitors memory usage and triggers jobs to reduce the size of each cache, before the available memory is exhausted. The jobs remove both cache entries and their associated metadata. The cache entries selected for removal are those that are sooner to expire.

### Inactive Maintenance (9.1.10+)
This job is not required for memory maintenance, but helps reduce the memory requirements by removing idle cache entries. Its design is very similar to that of expired maintenance, but for cache entries that haven't yet expired.
