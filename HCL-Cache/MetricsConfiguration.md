# HCL Cache Configurable Prometheus Metrics

The HCL Cache provides cache level configurations to customize the metrics created for the [Prometheus](Monitoring.md) integration. Although changes are not typically required, if you are integrating with a 3rd-party monitoring system and there is a cost associated with the retrieval or storage of metrics, these configurations can be used to fine-tune the metrics to be used.

## Cache configurations

Metrics are configurable at the cache level. Changes can be applied to a single cache, or to the default configuration using  `defaultCacheConfig`. See [cache configuration](CacheConfiguration.md) for details.

### Enabling or disabling metrics for a cache

Disable metrics for a cache using the `enabled` attribute as follows: 

```
  defaultCacheConfig:
    metrics:
      enabled: false
```

### Timer metrics histogram buckets

The `Timer` metrics used by the HCL Cache support [histograms](https://prometheus.io/docs/practices/histograms/) for the calculation of percentiles. 
The tracking of histogram values requires the definition of additional metrics. This support can be disabled to reduce the amount of metrics created.

```
hclcache_cache_clears_total{cachespace="demoqaauth",name="baseCache",scope="local",} 100.0
hclcache_cache_clears_duration_seconds_sum{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",} 1.3296758
hclcache_cache_clears_duration_seconds_max{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",} 0.0897587
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="1.0E-4",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="3.0E-4",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="5.0E-4",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="7.0E-4",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.001",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.003",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.005",} 0.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.01",} 23.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.05",} 99.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.1",} 100.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="0.5",} 100.0
hclcache_cache_clears_duration_seconds_bucket{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",le="+Inf",} 100.0
hclcache_cache_clears_duration_seconds_count{cachespace="demoqaauth",name="baseCache",result="ok",scope="remote",} 100.0
```
The default histogram configuration is as follows:

```
  defaultCacheConfig:
    metrics:
      timerNanoBuckets:
        - 100000 # 0.1 ms
        - 300000 # 0.3 ms
        - 500000 # 0.5 ms
        - 700000 # 0.7 ms
        - 1000000 # 1.0 ms
        - 3000000 # 3.0 ms
        - 5000000 # 5.0 ms
        - 10000000 # 10.0 ms
        - 50000000 # 50.0 ms
        - 100000000 # 100.0 ms
        - 500000000 # 500.0 ms
```
Values are in nanoseconds.

The histogram buckets can be disabled by specifying an empty list:

```
  defaultCacheConfig:
    metrics:
      timerNanoBuckets: []    
```

If disabled, percentile calculations will no longer be available in the `HCL Cache - Remote` Grafana dashboard.

## Use of common metrics for all caches

The number of metrics can also be reduced by using a combined `Timer` for all caches. This change is incompatible with the HCL Cache dashboards and can be inaccurate when with Redis cluster.

```
  defaultCacheConfig:
    metrics:
      addCacheNameLabelToTimers: false
```


