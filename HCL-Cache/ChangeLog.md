# Change Log

## HCL Commerce 9.1.10

- *Fix*: HC-14694 - Improve hcl-cache-benchmark messages when Redis is down (avoid NPE)
- *Fix*: HC-14782 - Don't call getMemoryUsagePercentageFromInfo when maxMemoryPercentage is not used
- *Fix*: HC-15596 - Nullpointer exception when DynaCache trace is enabled
- *Improvement*: HC-15129 - Adjustments to maintenance
- *Improvement*: HC-15154 - Use custom logic instead of Redisson Lock (used in LowMemoryMaintenance)
- *Feature*: HC-14863 - Implement sharding
- *Feature*: HC-16395 - Implement inactivity
- *Feature*: HC-16081 - New option for SSL: sslTruststore: "${WEBSPHERE_TRUSTSTORE_PATH}"

## HCL Commerce 9.1.9

- *Fix*: HC-12835 - Cannot set timeout longer than 30 days
- *Improvement*: HC-13285 - Implement HCL Cache subscribe watchdog
- *Improvement*: HC-11572 - LocalHclCache - Reduce time spent checking for expired entries
- *Improvement*: HC-13542 - Improve LocalHclCache Concurrency

## HCL Commerce 9.1.8

- *Fix*: HC-12605 - Invalidation messages missing when dependency id has less than 25 entries
- *Fix*: HC-12123 - Circuit Breakers for when Redis is not available during startup
- *Improvement*: Local Cache: Move timeout processing into a separate thread
- *Feature*: HC-11746 - Enable dependency directives (skip_local, skip_remote)
