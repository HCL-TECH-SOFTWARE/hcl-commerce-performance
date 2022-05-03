# Use of Cache Directives

The use of cache directives extends the [cache configuration](CacheConfiguration.md), to allow instructions to be applied at the cache entry level.
Cache Directives are disabled by default except for the baseCache as follows:

```
  baseCache:
    enableDirectives: true
```


## skip-local and skip-remote directives

The `skip-local` and `skip-remote` directives instruct the HCL Cache to not use the local or remote cache for this particular cache-id.
The directive must be included within the cache-id as follows:

- `hcl-cache:skip-remote`: *put* and *get* operations for this cache-id as done only on the local cache.
- `hcl-cache:skip-local`: *put* and *get* operations for this cache-id as done only on the remote cache.

These directives serve a specific use case where a cache enables both local and remote cache, but there is a preference for specific cache-ids to use only one cache.
For example, in cases of cache-entries with low reusability, you might choose to disable remote caching.

> HCL Commerce 9.1.10+ includes [Inactivity maintenance](RemoteCacheTuningConfigurations.md#inactivity-and-skip-remote-cache-directive), which can be enabled in the Remote Cache to discard cache entries that are not seeing reuse
> This enables efficient use of the remote cache, and remote caching might not need to be disabled.

### Use of skip-local and skip-remote directives in cachespec.xml

The `skip-local` and `skip-remote` directives can be specified in cachespec.xml by referring the matching request attribute:

- *DC_HclCacheSkipRemote*: special attribute that instructs the HCL Cache not to use remote cache for this entry even when enabled for the cache.
- *DC_HclCacheSkipLocal*: special attribute that instructs the HCL Cache not to use local cache for this entry even when enabled for the cache.
    
For caches that enable directives, cache entries that include the respective attributes will bypass local or remote caching as specified:

```    
<component id="DC_HclCacheSkipRemote" type="attribute">
   <required>true</required>
</component>
``` 


