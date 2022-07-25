# Bitnami Redis Installation

Although Redis is installed automatically as a sub-chart of HCL Commerce, it can also be installed separately, or with different configurations. This document describes the recommended deployment options and the use of Bitnami charts.

## Bitnami Redis install in HCL Commerce Helm Chart

The [HCL Commerce chart](https://github02.hclpnp.com/commerce-dev/commerce-helmchart/blob/master/hcl-commerce-helmchart/stable/hcl-commerce/values.yaml) can automatically setup Redis during install using the Bitnami Redis charts.

The default values for the Bitnami Redis chart are a minimal configuration for non-production use. For production environments, you should consider increasing the Redis memory ([maxmemory](#redis-configurations)) and matching Redis pod memory and CPU limits, and review if changes for *Transparent huge pages* or *Socket Max Connections* are required (see [Additional OS Configurations](#additional-os-configurations-sysctl)).

Additional considerations include more advanced tologies, such as Cluster, use of replicas, persistence, and monitoring.

## Installation Considerations:

### Topology
Redis can be installed with different topologies, including standalone, master/slave, sentinel or cluster. Most cloud providers also offer managed versions of Redis that 'hide' some of the high-availability and replication complexities.
The following are recommended configurations using the Bitnami charts:
- *standalone:* A single master with no replicas can work well in many scenarios. As the HCL Cache is a multi-tiered framework, the most frequently-accessed content is served from local caches, reducing the load on Redis and its capacity requirements (the load will vary from site to site depending on the amount of caching and hit ratios). 
The HCL Cache is also designed with high availability features, and implements circuit breakers that block Redis access until the server recovers. During that time, the local caches remain available.
The Redis deployment defines probes, and Kubernetes will detect hang or crash situations and quickly re-spawn the master container.  Note that if replicas/slaves were defined (without Sentinel), the replicas are for ready-only access and are not promoted to master. The system still needs to wait for the master to be re-spawned.
See [topologies](https://github.com/bitnami/charts/tree/master/bitnami/redis#cluster-topologies) for more details.
- *cluster:*  Redis cluster requires a minimum of 3 master servers. HCL Caches are distributed across the different master nodes.
[Sharding](RemoteCacheTuningConfigurations.md#sharding) can also be used to partition a cache across nodes. If replicas are used, 6 containers need to be deployed. Replicas can be used for failover and to handle read traffi. See [Redis Replicas](RedisReplicas.md) for details.

See the [Redis Cluster tutorial](https://redis.io/topics/cluster-tutorial) for more details.

### Persistence

Redis offers [persistence](https://redis.io/topics/persistence) (AOF/RDB) options that save the memory contents to disk. This allows Redis to recover the memory contents (cache) in case of a crash. 

With standalone Redis, the use of Persistence is optional but with Redis cluster it is recommended. The use of persistence can add a small overhead to runtime operations.
There can also be a delay during Redis startup as it loads the persisted cache into memory. This delay varies depending on the size of the file.
For use with HCL Cache, use of RDB only (not AOF) can be sufficient.

When configuring Kubernetes persistent volumes for Redis, select a storageClass with fast/SSD storage. By default, Redis requests only 8GB of storage for a persistant volume.
That may not be enough, especially if AOF persistence is enabled. Request a larger size (e.g. 30GB) and monitor usage to get a better understanding for how much
storage is required.

## Redis Bitnami Charts

[Bitnami](https://github.com/bitnami/charts/) publishes the most popular Redis charts, and they can be used to install Redis within the Kubernetes cluster.

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Redis Standalone

Use this [Redis chart](https://github.com/bitnami/charts/tree/master/bitnami/redis) to install Redis standalone, with no persistence. Review [redis-standalone-values.yaml](samples/redis-standalone-values.yaml) for details.

```
helm install hcl-commerce-redis bitnami/redis -n redis -f redis-standalone-values.yaml
```

_Note: If Prometheus is not setup, disable the metrics section prior to install_

### Redis Cluster

These steps install a [Redis Cluster](https://github.com/bitnami/charts/tree/master/bitnami/redis-cluster) with three masters. Review [redis-cluster-values.yaml](samples/redis-cluster-values.yaml) For details.

```
helm install hcl-commerce-redis bitnami/redis-cluster -n redis -f redis-cluster-values.yaml
```

_Note: If Prometheus is not setup, disable the metrics section prior to install_

## Configurations and settings

### Redis Configurations
The `configuration` section of the chart allow to pass configuration options to [redis.conf](https://raw.githubusercontent.com/antirez/redis/6.2/redis.conf). This file is self-documented and you should review it to get familiar with the different configurations.

```
  configuration: |-
    appendonly no
    save ""
    maxmemory 10000mb
    maxmemory-policy volatile-lru
```

*maxmemory*: Determines the size of the memory available to store Redis objects. The amount of cache will vary from site to site. 10GB is a good starting configuration. The pod memory limit must be higher. 

*maxmemory-policy*: Using _volatile-lru_ is required for the HCL Cache. This allows Redis to evict cache entries but not dependency ids.
The options *appendonly* and *save* are for [persistence](https://redis.io/topics/persistence), which is disabled in the sample. 

This section can also be used to enable debug setting such as for [SLOWLOG](https://redis.io/commands/slowlog):

```
slowlog-log-slower-than 10000
slowlog-max-len 512    
latency-monitor-threshold 100
```
Redis Cluster only:
- *cluster-require-full-coverage: no*: When not all of the slots are covered (e.g. due to master down), the CLUSTERDOWN error is issued. Configuring *cluster-require-full-coverage* to *no* enables the subset of nodes that remain available to continue to serve requests.

If you plan to enable replicas, see [Use of Redis Replicas](RedisReplicas.md) for additional configurations.

### Persistence
Kubernetes persistence (PVC) must be enabled if Redis persistence (AOF/RDB) is used, or with Redis clustering. If Redis persistence is used, the PVC must be large enough to accommodate the Redis memory dumps.
With Redis Cluster, the cluster maintains a _nodes.conf_ file that must persist, as otherwise nodes that restart are unable to re-join the cluster. This file requires
minimal storage.

### Resources
Redis is single-threaded (for the most part) and it benefits from faster processors. Two CPUs can work well in many scenarios. It's important to monitor for Kubernetes CPU  throttling and ensure it is not happening, as throttling can 'hang' the Redis main thread. 

Configuring the memory limit so that `maxmemory` is 50-70% of the container limit is a good starting point. Memory utilization for the pod should be monitored. For example, usage can peak when replicas are used and during replication, and if the memory limit is exceeded, Kubernetes might kill the Redis container (OOMKill). See [Redis Replicas](RedisReplicas.md#redis-configurations) for details.

```
 resources:
    limits:
      cpu: 2000m
      memory: 12Gi
    requests:
      cpu: 2000m
      memory: 12Gi
```
### Metrics
If Prometheus is setup, you can enable metrics and serviceMonitors (requires [kube-prometheus-stack](../../Grafana/PrometheusGrafanaInstall.md)).
Redis metrics can be consumed with the [Redis Grafana dashboard](https://grafana.com/grafana/dashboards/11835). The  _HCL Cache - Remote_ dashboard also displays Redis metrics.

```
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    namespace: redis
``` 
### Additional OS configurations (sysctl)
Redis requires certain host level configurations to perform well. These may or may not be required depending on the node configurations.
See [Configure Host Kernel Settings](https://docs.bitnami.com/kubernetes/infrastructure/redis/administration/configure-kernel-settings/) for more details.

*Transparent huge pages:* If enabled, you will see this warning in the Redis log:
```
WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command 'echo madvise > /sys/kernel/mm/transparent_hugepage/enabled' as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled (set to 'madvise' or 'never').
```
The configuration can be checked from within the Redis container with this command:
```
cat /sys/kernel/mm/transparent_hugepage/enabled
```
*Socket Max Connections (somaxconn):* If missconfigured, the following warning can be printed to the logs:
```
WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
```
The current value can be validated as follows:
```
cat /proc/sys/net/core/somaxconn
```
Add this section on the values.yaml file to configure THP and somaxconn as follows:

```
sysctl:
  enabled: true
  mountHostSys: true
  command:
    - /bin/sh
    - -c
    - |-
      sysctl -w net.core.somaxconn=10240
      echo madvise > /host-sys/kernel/mm/transparent_hugepage/enabled
```
