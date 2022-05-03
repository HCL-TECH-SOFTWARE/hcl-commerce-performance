# HCL Cache - Circuit Breakers

HCL Cache implements circuit breakers for the remote cache to protect the application from a failing or unavailable Redis server. 
If a circuit breaker detects a Redis server is failing, it prevents new requests to the Redis server for a period of time. 
Circuit breakers are used in addition to high availablity configurations provided by Kubernetes and Redis itself, such as replicas.

**Local Caches**: As invalidation messages can neither be sent nor received during a Redis outage, local caches implement a shorter timeout for new and existing entries. By default, the timeout during outages is configured to 5 minutes.

**Remote Only Caches**: Remote only caches become unavailable during a Redis outage.

The default configuration can be interpreted as follows: "If there are at least 20 consecutive failures (*minimumConsecutiveFailures*), over a period of at least 10 seconds (*minimumFailureTimeMs*), break the circuit (prevent new connections) for 1 minute (*retryWaitTimeMs*). After that time, allow new queries to Redis, but if the first 2 requests (*minimumConsecutiveFailuresResumeOutage*) continue to fail, break the circuit again for another minute".

### Redis request time out

Slow Redis requests are not considered failures unless they time out. The [Redis Client](RedisClientConfig.md) has configurations for timeouts and retry attempts including:

```
  timeout: 3000
  retryAttempts: 3
  retryInterval: 1500
``` 

Considering retries, with the configuration above a request will need 16.5 seconds before returning in failure (3000+3*(3000+1500)). Timeouts can be made more aggresive but that could lead to sporadic errors in the logs. 

### Circuit breaker configurations

Circuit breaker configurations can be adjusted using the [Cache YAML](CacheConfiguration.md) configuration. 

The configuration for the circuit breaker is available under `redis`, `circuitBreaker`. The maximum timeout for local caches in outage mode is configured using the
`maxTimeToLiveWithRemoteOutage` element under `localCache` as in the following example: 

```
redis:
  circuitBreaker:
    scope: auto
    retryWaitTimeMs: 60000
    minimumFailureTimeMs: 10000
    minimumConsecutiveFailures: 20
    minimumConsecutiveFailuresResumeOutage: 2
cacheConfigs:
  defaultCacheConfig:
    localCache:
      enabled: true
      maxTimeToLiveWithRemoteOutage: 300   
```

Setting | Default | Use
--- | --- | ---
scope | auto | Depending on the topology, circuit breakers must be configured at the client (single circuit breaker configuration for all), or cache/shard level. HCL Cache automatically selects the scope depending on the configuration used: *cache* level is used when the topology is cluster, and either Commerce fails to connect to Redis during startup, or the setting *cluster-require-full-coverage* is set to false. Otherwise the scope is set to *client*.
minimumConsecutiveFailures | 20 | The minimum number of consecutive connection attempt failures before a cache can be set in outage mode. This value, and minimumFailureTimeMs must be satisfied before the circuit breaker breaks the Redis connection. Notice that any successful operation resets this counter.
minimumFailureTimeMs	|  10000 (10 seconds) | The time, in milliseconds, that must elapse before a cache can be put into outage mode. This amount of time, and minimumConsecutiveFailures must be satisfied before the circuit breaker breaks the Redis connection.
retryWaitTimeMs |	60000 (60 seconds)| Once a cache is set in outage mode, retryWaitTimeMs is the time, in milliseconds, that must elapse before the Redis connection is retried.
minimumConsecutiveFailuresResumeOutage	| 2 |  The minimum number of consecutive connection attempt failures before a cache can be set back into outage mode. When a connection is in outage mode and reaches the retryWaitTimeMs value, the circuit breaker will allow connection attempts to the Redis server. In order to allow for quick testing of the connection without an undue excess of connection attempts, the minimumConsecutiveFailuresResumeOutage is used. If minimumConsecutiveFailuresResumeOutage is reached, the connection is placed back into outage mode, without having to wait for the entire minimumFailureTimeMs and minimumConsecutiveFailures condition cycle to be satisfied once again. 



