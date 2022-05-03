# HCL Cache - Caching and Redis Client Configurations

The HCL Cache is configured via a set of files that define the configurations for each cache, and the Redis connection information:

File | Location | Usage
--- | --- | --- |
/SETUP/hcl-cache/redis_cfg.yaml | Config Map | Redis client connection information
/SETUP/hcl-cache/cache_cfg.yaml | Container | Provided out of the box and present on all containers that use the HCL Cache. It contains default and out of the box configurations and must not be modified
/SETUP/hcl-cache/cache_cfg-ext.yaml | Config Map | Customers can create this file to extend and override the configuration in cache_cfg.yaml. This file has the same format as cache_cfg.yaml

### Redis client configuration

The Redis client connection information is stored in redis_cfg.yaml. This file contains details about the topolgy (standalone, cluster, etc), the connection information (hostname, TLS, authentication), pools and timeouts.  See [Redis Client Configuration](RedisClientConfig.md) for details.

### Cache configurations

Caches are configured in two main files: `cache_cfg.yaml` exists on all contains and defines default values, and specific values for out of the box caches, and `cache_cfg-ext.yaml` can be used to update defaults or set new configurations for custom caches.  See: [Cache Configuration](CacheConfiguration.md).

## Configurations in Kubernetes 

For customizable files (cache_cfg-ext.yaml and redis_cfg.yaml), the HCL Cache uses a technique whereby the contents of the files are stored in Kubernetes Configuration Maps (configmap). This allows for updates to be made without having to create custom images for each environment, as for example the Redis hostname might be different from environment to environment. Pods are configured to load the config map during initialization and make its contents available as regular files.

### Configurations in Helm

The `configmaps` are originally created during installation of the Helm chart. The original values are defined in the `hclCache` section of [values.yaml](https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-helmchart/blob/master/hcl-commerce-helmchart/stable/hcl-commerce/values.yaml#L296). These values can be updated as required.

```
hclCache:
  configMap:
    cache_cfg_ext: |-
      redis:
        enabled: true
        yamlConfig: "/SETUP/hcl-cache/redis_cfg.yaml" # Please leave this line untouched
      cacheConfigs:
       ...
    redis_cfg: |-
      singleServerConfig:
        ...
```

To update the configuration, the recommended approach is to update the chart, and perform `Helm Update`. If the configmap is updated directly, pods must be manually restarted to load the updated values.

*Important:* Change to one release (auth/share/live) might need to be repicated to the others.  

### Validating the current client configuration

After installation, you can inspect the contents of the `configmap` as follows:

```
kubectl get configmap -n commerce
NAME                                    DATA   AGE
demo-qa-auth-demoqa-hcl-cache-config    2      15d
demo-qa-live-demoqa-hcl-cache-config    2      15d
demo-qa-share-demoqa-hcl-cache-config   2      15d
```

```
kubectl describe configmap -n commerce demo-qa-auth-demoqa-hcl-cache-config
kubectl edit configmap -n commerce demo-qa-auth-demoqa-hcl-cache-config
```

