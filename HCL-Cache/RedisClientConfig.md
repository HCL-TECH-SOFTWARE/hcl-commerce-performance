# HCL Commerce - Redis Client configurations

HCL Commerce uses the [Redisson](https://github.com/redisson/redisson) client to communicate with the Redis server. Redisson is configured using a YAML configuration file, which is defined in the HCL Commerce Helm chart and stored in a Kubernetes config map.

The Redisson YAML configuration needs to be customized to:
- Match the topology of the Redis server (standalone, cluster)
- Specify the Redis server hostnames
- Tune pools and retries
- Configure security options (password, SSL)

### Connection options:

#### Authentication
If the Redis server enables authentication (password), the password can be specified in the Yaml configuration file.

Create a Vault key `redisPasswordEncrypt` under the environment type (for example qa or prod). The password must be encrypted using  [wcs_encrypt](https://help.hcltechsw.com/commerce/9.1.0/admin/refs/rwcs_encrypt.html).
 
```
password: "${ENCRYPTED:REDIS_PASSWORD_ENCRYPT:-}"
```

Alternatively, the password can be entered in plain text (not secure), or stored encrypted in an environment variable named *REDIS_PASSWORD_ENCRYPT*.

#### TLS
The Redis client can be configured to access a Redis service that uses SSL/TLS. For details: [Redis With TLS](RedisWithTLS.md).


## Sample Configuration files:

This external document provides details on the client configuration settings: [Redisson - Configuration](https://github.com/redisson/redisson/wiki/2.-Configuration/)

- Standalone Redis: [singleServerConfig.yaml](samples/singleServerConfig.yaml)
- Redis Cluster: [clusterServersConfig.yaml](samples/clusterServersConfig.yaml)

## Redis Client Configuration in Commerce

The Redis client configuration is defined in 
[values.yaml](https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-helmchart/blob/master/hcl-commerce-helmchart/stable/hcl-commerce/values.yaml#L296) as described in the
[Configuration](Configuration.md) document. 

```
hclCache:
  configMap:
    # content for cache_cfg-ext.yaml
    cache_cfg_ext: |-
      redis:
        enabled: true
        yamlConfig: "/SETUP/hcl-cache/redis_cfg.yaml" # Please leave this line untouched
    # content for redis_cfg.yaml
    redis_cfg: |-
      singleServerConfig:
        idleConnectionTimeout: 10000
        connectTimeout: 3000
        timeout: 1000
  ...
```
