# HCL Cache Configurations

The HCL Cache provides a set of configuration files in [YAML](https://en.wikipedia.org/wiki/YAML) format. The configuration can be updated for tuning purposes, or to provide custom caches with non-default configurations. See [Configurations in Helm](Configuration.md#configurations-in-helm) for details on how the configuration is updated. 

File | Location | Usage
--- | --- | --- |
/SETUP/hcl-cache/cache_cfg.yaml | Container | Created out-of-the-box and present on all containers that use the HCL Cache. It contains default and out-of-the-box configurations and must not be modified. 
/SETUP/hcl-cache/cache_cfg-ext.yaml | Config Map | Extends and overwrites the configuration in cache_cfg.yaml. This file maintains the same format as cache_cfg.yaml.

> cache_cfg.yaml must not be modified. All customizations should be done using cache_cfg-ext.yaml and the steps documented in [Configurations in Helm ](Configuration.md#configurations-in-helm).

## Configuration merging process

During initialization, each container performs a merging process using the out-of-the-box configuration file (/SETUP/hcl-cache/cache_cfg.yaml), and the extensions file (/SETUP/hcl-cache/cache_cfg-ext.yaml) which is created from the Kubernetes' configuration map. The extensions file can be used to configure custom caches with non-default values, or to change default configurations.

> When overwriting list elements, such as for maintenance configurations, you must overwrite the complete list

### Default cache configurations - defaultCacheConfig

The `defaultCacheConfig` element defines default configurations. Custom and out-of-the-box caches that are not explicitly defined in the YAML configurations take their configuration from `defaultCacheConfig`.  If a cache is defined in the configuration file, configuration elements that are not explicitly specified use defaults from `defaultCacheConfig`. The `defaultCacheConfig` can be overwritten using the `cache_cfg-ext.yaml` (extension file). While `defaultCacheConfig` makes it easier to implement changes that apply to all caches, cache specific changes should be done at the cache level.

### Example: Custom remote only cache

The default configuration enables [local and remote caching](LocalAndRemoteCaching.md). A [custom](CustomCaching.md) remote-only cache can be defined by adding the cache under the `cacheConfigs` element, and setting `enabled: false` for the `localCache` element as follows:

```
cacheConfigs:
  ...
  services/cache/MyCustomCache:
    remoteCache:
      enabled: true  
    localCache:
      enabled: false
```

