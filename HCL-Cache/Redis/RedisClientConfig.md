# HCL Commerce - Redis Client configurations

HCL Commerce uses the [Redisson](https://github.com/redisson/redisson) client to communicate with the Redis server. Redisson is configured using a YAML configuration file, which is defined in the HCL Commerce Helm chart and stored in a Kubernetes config map.
The Redisson YAML configuration needs to be customized to:
- Match the topology of the Redis server (standalone, cluster)
- Specify the Redis server hostnames
- Tune pools and retries
- Configure security options (password, SSL)

## Sample Configuration files:

- Standalone Redis: [singleServerConfig.yaml](singleServerConfig.yaml)
- Redis Cluster: [clusterServersConfig.yaml](clusterServersConfig.yaml)

## HCL Commerce Chart - values.yaml

The *hclCache* element in the HCL Commerce chart allows you to customize the configuration map prior to install, or for helm upgrade.

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

## Validating the current client configuration

The Redis client configuration is stored in Kubernetes configuration maps. The contents of the configuration maps are mounted as volumes and made available to the Commerce pods.

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
*Important:* If you make changes to one configmap, replicate the same changes on the other.




