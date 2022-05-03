# Troubleshooting the HCL Cache

This page lists tools and techniques that can be used for troubleshooting the cache:

- [Monitoring](#Monitoring)
- [Cache Manager](#Cache-Manager)
- [Redis database](#Redis-Database)
- [Tracing](#Tracing)

## Monitoring
Debugging a complex distributed system without the support of metrics and monitoring can be a challenging task. The [Prometheus and Grafana](Monitoring.md) integration gives you visibility into the number and performance of all cache operations and maintenance processes, which can enable you to quickly narrow down the problem.

## Cache Manager
The Cache Manager includes a number of debug APIs to retrieve details about the caches and cached data. See [Cache Manager](CacheManager.md) for details.

## Redis Database
Redis is a database, and a such it provides a command interface (redis-cli) and [commands](https://redis.io/commands/) that can be used to query it and retrieve information about the existing cache keys and metatada. For details see [HCL Cache in Redis](HCLCacheInRedis.md).

## Tracing
The following string is used to trace the operation of the HCL Cache:
```
com.hcl.commerce.cache*=all
```
If enabled at the `fine` level instead, the HCL Cache will create a less verbose output, with timing and invalidation details.

# Troubleshooting Scenarios

- [Near-Real-Time (NRT) Build Index](Troubleshooting-NRT.md)



