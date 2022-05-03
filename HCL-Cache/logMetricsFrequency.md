# HCL Cache configuration: logMetricsFrequency

The `logMetricsFrequency` configuration option can be used to specify, in seconds, the frequency at which cache statistics are written to the logs. This can be especially useful for environments where the [Prometheus and Grafana](Monitoring.md) integration is not available.

## Enabling logMetricsFrequency

The `logMetricsFrequency` setting is a top level configuration option. See [cache configuration](CacheConfiguration.md) for details.

```
apiVersion: v1
data:
  cache_cfg-ext.yaml: |-
    redis:
      enabled: true
      yamlConfig: "/SETUP/hcl-cache/redis_cfg.yaml" # Please leave this line untouched
    logMetricsFrequency: 60
    cacheConfigs:
      baseCache:
        remoteCache:
          shards: 5
  redis_cfg.yaml: |-
     ...
```

## Cache metrics loggers

Cache metrics are printed to the logs in the frequency set by `logMetricsFrequency` using the `com.hcl.commerce.cache.MetricsLogger` logger and `INFO` level:

```
[5/2/22 16:05:08:697 GMT] 000000ed CacheMetrics  I baseCache {"[demoqaauth]:baseCache":{"remote":{"invalidates.duration.result.ok":"1/0.0075 secs- avg: 7.49 ms","puts.duration.result.ok":"1500/5.2514 secs- avg: 3.50 ms","clears.duration.result.ok":"1/0.0852 secs- avg: 85.17 ms"},"local":{"size.current":"1500","puts.source.local":1500,"clears":1,"size.current.max":"5000","size.max":"5000"}}}
```

Formatted JSON output:

```
{
	"[demoqaauth]:baseCache": {
		"remote": {
			"invalidates.duration.result.ok": "1/0.0075 secs- avg: 7.49 ms",
			"puts.duration.result.ok": "1500/5.2514 secs- avg: 3.50 ms",
			"clears.duration.result.ok": "1/0.0852 secs- avg: 85.17 ms"
		},
		"local": {
			"size.current": "1500",
			"puts.source.local": 1500,
			"clears": 1,
			"size.current.max": "5000",
			"size.max": "5000"
		}
	}
}
```

