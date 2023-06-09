# HCL Cache - Circuit Breakers

HCL Cache implements circuit breakers for the remote cache to protect the application from a failing or unavailable Redis server. 
If a circuit breaker detects a Redis server is failing, it prevents new requests to the Redis server for a period of time. 
Circuit breakers are used in addition to high availablity configurations provided by Kubernetes and Redis itself, such as replicas.

**Local Caches**: As invalidation messages can neither be sent nor received during a Redis outage, local caches implement a shorter timeout for new and existing entries. By default, the timeout during outages is configured to 5 minutes.

**Remote Only Caches**: Remote only caches become unavailable during a Redis outage.

The default configuration can be interpreted as follows: "If there are at least 20 consecutive failures (*minimumConsecutiveFailures*), over a period of at least 10 seconds (*minimumFailureTimeMs*), break the circuit (prevent new connections) for 1 minute (*retryWaitTimeMs*). After that time, allow new queries to Redis, but if the first 2 requests (*minimumConsecutiveFailuresResumeOutage*) continue to fail, break the circuit again for another minute".

### Redis request time-out

Slow Redis requests are not considered failures unless they time out. The [Redis Client](RedisClientConfig.md) has configurations for timeouts and retry attempts including:

```
  timeout: 3000
  retryAttempts: 3
  retryInterval: 1500
``` 

Considering retries, with the configuration above a request will need 16.5 seconds before returning in failure (3000+3*(3000+1500)). Timeouts can be made more aggresive but that could lead to sporadic errors in the logs. 

### Circuit breaker configurations (9.1.12+)

HCL Commerce 9.1.12 introduces new circuit breaker logic based on the [Resilience4j](https://resilience4j.readme.io/docs/circuitbreaker) library. This library has the advantage that besides tracking success and failure conditions (e.g. if the request ended in error), it can also trigger based on increased response times.

9.1.12+ environments automatically use the new implementation unless the original circuit breaker configurations in the YAML file has been customized.
If the original circuit breaker configuration is using non-default values, the original implementation will be used instead. To use the new implementation,
remove the circuit breaker configurations from the YAML configuration.

Circuit breaker configurations can be adjusted using the [Cache YAML](CacheConfiguration.md) configuration. The new format allows defining of multiple circuit breaker configurations. The default configuration must always exist.

```
redis:
  enabled: true  
  yamlConfig: "C:/dev/projects/redis/maven/workspace/redis-cache/config/redis_cfg.yaml"
  circuitBreakerV2:
     enabled: true
     scope: auto
     configurations:
     - name: default
       waitDurationInOpenStateSeconds: 60
       failureRateThreshold: 50
       minimumNumberOfCalls: 20
       slidingWindowType: COUNT_BASED
       permittedNumberOfCallsInHalfOpenState: 2
       slowCallRateThreshold: 100
       slowCallDurationThresholdMs: 500
       slidingWindowSize: 50
```

Besides the configurations at the Redis client level, it's also possible to configure circuit breakers at the cache level. Use *false* to disable the circuit breaker
for a particular cache, or specify the name of a circuit breaker configuration as defined under the `redis.circuitBreakerV2.configurations` element. If a non-default
configuration is specified, the cache will use a cache level circuit breaker regarless of the scope defined in the Redis client.

```
 "services/cache/MyCustomCache":
    remoteCache:
      enabled: true
      useCircuitBreaker: agressive_timeout
```
#### Resilience4j Circuit Breaker states

State | Use
--- | ---
*CLOSED* | The Circuit Breaker is not in use
*OPEN* | The Circuit Breaker is active and requests are prevented from making calls to the remote cache
*HALF_OPEN* | The Circuit Breaker switches to HALF_OPEN state after it has been in OPEN state for the time specified by *waitDurationInOpenStateSeconds*. The HALF_OPEN state allows for a quicker verification to determine if the Circuit Breaker should remain in OPEN state, or if the remote cache recovered, move to CLOSE state. The *permittedNumberOfCallsInHalfOpenState* configuration determines how many requests are used to evaluate if the Circuit Breaker should remain open

Note: Prior to 9.1.13, the logic allowed a Circuit Breaker in HALF_OPEN state to issue multiple remote calls until a success or failure was reported. In 9.1.13 the connection verification logic was improved to only allow the number of calls specified by *permittedNumberOfCallsInHalfOpenState* to be issued. 

#### Resilience4j Configurations

The configurations under the `redis.circuitBreakerV2.configurations` element are standard from the [resilience4j-circuitbreaker](https://resilience4j.readme.io/docs/circuitbreaker#create-and-configure-a-circuitbreaker) library. Their usage is as follows:
 
Setting | Default | Use
--- | --- | ---
waitDurationInOpenStateSeconds | 9.1.12: 60, 9.1.13+:30  | Configures an interval function with a fixed wait duration which controls how long the CircuitBreaker should stay open, before it switches to half open. |
failureRateThreshold | 50 | Configures the failure rate threshold in percentage. If the failure rate is equal to or greater than the threshold, the CircuitBreaker transitions to open and startshort-circuiting calls. The threshold must be greater than 0 and not greater than 100.
minimumNumberOfCalls | 20 | Configures the minimum number of calls which are required (per sliding window period) before the CircuitBreaker can calculate the error rate.  For example, if minimumNumberOfCalls is 10, then at least 10 calls must be recorded, before the failure rate can be calculated. If only 9 calls have been recorded,  the CircuitBreaker will not transition to open, even if all 9 calls have failed.
slidingWindowType | COUNT_BASED | Configures the type of the sliding window which is used to record the outcome of callswhen the CircuitBreaker is closed. Sliding window can either be count-based or time-based.
permittedNumberOfCallsInHalfOpenState | 2 | Configures the number of permitted calls when the CircuitBreaker is half open. The size must be greater than 0. 
slowCallRateThreshold | 100 | Configures a threshold in percentage. The CircuitBreaker considers a call as slow when the call duration is greater than slowCallDurationThresholdMs. When the percentage of slow calls is equal to or greater than the threshold, the CircuitBreaker transitions to open and starts short-circuiting calls.  The threshold must be greater than 0 and not greater than 100. Default value is 100 percentage which means that all recorded calls must be slower than  slowCallDurationThresholdMs.
slowCallDurationThresholdMs | 9.1.2: 500, 9.1.13+: 250 | Configures the duration threshold above which calls are considered as slow and increases the slow calls percentage. 
slidingWindowSize | 50 |  Configures the size of the sliding window which is used to record the outcome of calls when the CircuitBreaker is closed.

### Circuit breaker configurations (9.1.11 and earlier)

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



