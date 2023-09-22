# Invalidation Support

Local caches require a mechanism for replication of invalidation messages to ensure that local cache entries associated to an invalidation id are removed from all  containers.

In Commerce V8, the IBM Data Replication Service (DRS) is integrated with WebSphere DynaCache and performs the job of replicating invalidation messages. In V9.0, Kafka is used to send invalidation messages. With HCL Cache with Redis in Commerce 9.1, replication of invalidation messages is handled within DynaCache by the HCL Cache Provider. HCL Cache automatically issues invalidation messages when `clear` and `invalidate` operations are issued for a cache that enables local caching. The same cache on other containers implement a listener, and when the invalidation messages are received, the indicated invalidate and clear operations are performed on the local cache.

HCL Cache relies on [Redis PUBSUB](https://redis.io/docs/manual/pubsub/) technology to replicate invalidation messages. Each cache defines a topic, with format `{cache-namespace-cacheName}-invalidation` where invalidation messages are issued and received.

The Redis database provides [commands](https://redis.io/commands/), that allow you to list listeners ([PUBSUB CHANNELS](https://redis.io/commands/pubsub-channels/)), 
publish ([PUBLISH](https://redis.io/commands/PUBLISH)) and subscribe to messages ([SUBSCRIBE](https://redis.io/commands/subscribe)). See [Invalidations in Redis](HCLCacheInRedis.md#invalidations) for details.

## Timing Considerations

Sending and receiving invalidation messages using Redis is fast, but not instantaneous.  Consider an HCL Commerce request that executes in the ts-app server and makes a change to data in the database.  Immediately after the database transaction commits, the local cache is invalidated and invalidation messages are sent to peer application servers.  Meanwhile, the application may execute a subsequent request that expects to use the updated data.  When the messages are received by the peer servers, they are immediately processed and local cache is invalidated according to the messages received.  But between the time that the messages are sent and the time that the local caches are invalidated, the data in the local caches is "stale".  If the subsequent request is received in a peer server before the cache invalidation has completed, it will see the stale data, perhaps causing incorrect processing to occur.

To help avoid accessing stale data due to this situation, the HCL Commerce data cache provides optional configurations to introduce a short delay in the original ts-app request, just after the invalidation messages are sent, and before the request returns.  If the delay is long enough to allow the invalidation messages to be completely processed in peer application servers, the timing problem can be avoided.

The delayAfterInvalidationMilliseconds data cache configuration can be used to specify how long a delay should be introduced.  But it may be difficult to estimate how much delay should be introduced.  The additional delayAfterInvalidationPercentBuffer configuration can be used to add an additional delay that is based on how long it typically takes to send and receive an invalidation message.  This setting only has effect when the delayAfterInvalidationMilliseconds is greater than zero.  These settings can be specified on a global level, or can be specified for only certain logical caches.  For more information about these settings, see: [HCL Commerce 9.1 Help - Additional HCL Commerce data cache configuration](https://help.hcltechsw.com/commerce/9.1.0/admin/concepts/cdcaddcomdatcacheconfig.html).

For example, if occasionally accessing stale data is unacceptable, specifying delayAfterInvalidationMilliseconds="1" and delayAfterInvalidationPercentBuffer="100" would insert a delay of 1 millisecond plus twice the length of time it typically takes to send and receive a message.  That should be more than enough time to avoid the possibility of accessing stale data.

## Gradual Local Cache Invalidation

> Gradual local cache invalidation is available since 9.1.14.

Clearing an active cache can have a sudden impact on application server performance while the number of concurrent cache misses suddenly increases dramatically.  As the cache warms up, server performance gradually returns to normal.  A similar effect occurs when an invalidation message causes a large percentage of a cache to be invalidated.

Since version 9.1.14 of the HCL Cache, invalidation ids can be prefixed with delay information that can be used to invalidate local cache entries more gradually, and a new cache clear invalidation with similar delay information can be used to invalidate all existing local cache entries more gradually.

Note that the delay information only applies to local cache entries--remote caches ignore the delay information, and their cache entries are invalidated immediately.

To gradually invalidate all local cache entries with a dependency id of "product:1234" over the next 120 seconds (corresponding remote cache entries are invalidated immediately), specify a specially prefixed invalidation id like this:

```
delay(120000)product:1234
```

Or, to first wait one minute and then gradually invalidate the local cache entries, specify:

```
delay(60000,120000)product:1234
```

To gradually invalidate all cache entries currently in the local cache, use the new cache clear invalidation message, like this:

```
clear(120000)
```

or to first wait one minute before gradually clearing the local cache, specify:

```
clear(60000,120000)
```

When local caches are invalidated more gradually, the impact on server performance is reduced, as there are fewer concurrent cache misses at any one time.

## Local Cache Least Recently Used Eviction

When adding a new cache entry to a cache that has already reached its maximum capacity (either in number of entries or maximum footprint), and the maximum capacity cannot be automatically increased (see [Automatic Memory Footprint Tuning](LocalCacheAutoTuning.md)), the least recently used (LRU) cache entry in that cache is removed before the new cache entry is added.

Starting in version 9.1.14, most local caches can be configured with a new globalLRUEviction configuration.  When Automatic Memory Footprint Tuning is enabled and the amount of free memory in the JVM heap is too low to allow the maximum capacity to be automatically increased, local caches with this configuration enabled may also evict some of their cache entries (even if they have not yet reached their maximum capacity) when another local cache experiences LRU eviction while adding a new cache entry.  The cache entries to be evicted by this configuration are the least recently used cache entries selected from all the caches with the globalLRUEviction configuration enabled.  When enough memory is made available in this manner, [Automatic Memory Footprint Tuning](LocalCacheAutoTuning.md) can increase the maximum capacity for all caches, avoiding LRU evictions from more active caches.  By sharing the available memory in this way, local caches with the globalLRUEviction configuration enabled can make more efficient use of memory.

#### Configuring global LRU eviction

> Global LRU eviction is available since 9.1.14. It is disabled by default.

The globalLRUEviction configuration can be used to configure local caches that can tolerate LRU eviction even when they have not reached their maximum capacity.
```
cacheConfigs:
  services/cache/MyCustomDistributedMapCache:
    localCache:
      globalLRUEviction: true
```

