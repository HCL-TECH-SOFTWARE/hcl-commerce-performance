# HCL Cache - Implementation

The following steps guide you thru the step and options for implementing the HCL Cache with Redis. 

### 1- Implement monitoring

Although the use of [monitoring with Prometheus and Grafana](Monitoring.md) is not mandatory, its use is critical for tuning, and ensuring correct functioning of the cache in production. The HCL Cache defines a comprehensive set of monitoring metrics, which provides detailed insight into cache operation and performance. These metrics can be consumed in Prometheus and displayed with the supplied Grafana dashboards. It is also possible to integrate 3rd-party monitoring to consume the HCL Cache Prometheus-style metrics, but that requires additional configuration.

### 2 - Select a Redis configuration

Redis can be installed in a variety of configurations, depending on your performance and high-availability requirements. Alternatives include using the Bitnami Charts to install within the Kubernetes cluster, using Redis Enterprise by RedisLabs, or using Redis as-a-service from a cloud provider. Redis can be installed standalone, or clustered with replicas. Review the [Redis Server](RedisServer.md) guide for details.

> This is also a good time to familiarize yourself with Redis and its use by the HCL Cache. See [Memory management](RedisMemoryManagement.md) and [HCL Cache in Redis](HCLCacheInRedis.md) for details.

### 3 - Configure the Redis client in HCL Commerce

The Redis client configuration in HCL Commerce must be updated to match your Redis server setup. The Redis client is configured with a YAML file that contains information about the topology (standalone, cluster, etc), the Redis end-points, TLS and authentication options, and time-outs and thread pool options. The Redis client can be configured in
[values.yaml](https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-helmchart/blob/87e05746dc4e5b412c663c858d180edcf2723e12/hcl-commerce-helmchart/stable/hcl-commerce/values.yaml#L317) and it is stored in a Kubernetes config map.  See [Redis Client Config](RedisClientConfig.md) for details.

### 4 - Caching configurations for custom caches

As the HCL Cache is implemented as a DynaCache Cache Provider, custom caches are enabled for HCL Cache. Caches, by default, enable local and remote caching. Depending on your requirements, you can re-configure custom caches to be local-only, or remote-only. See [Cache Configurations](CacheAndRedisClientConfiguration.md) and [Custom Caching](CustomCaching.md) for details.

### 5 - Cache Tuning

Large implementations can benefit from additional cache tuning configurations. This can be done with the support of [Prometheus and Grafana](Monitoring.md) monitoring.
Large single caches, such as baseCache, can be sharded so they can be distributed among multiple Redis masters. Compression and inactivity options are also available to reduce the memory footprint of each cache. See [Remote Cache Tuning Configurations](RemoteCacheTuningConfigurations.md) for additional details.

