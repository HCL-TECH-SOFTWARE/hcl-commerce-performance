# HCL Cache in Redis

Redis is the remote database that stores HCL Cache data, and it is also used to replicate invalidations to local caches. For troubleshooting and adminstrative purposes, it might sometimes be required to use the Redis command line to query or configure the database.
This page includes a list of commands and concepts that you might find useful when learning or troubleshooting the cache system. For a complete list of comands check the [Redis site](https://redis.io/commands).

This document assumes you installed Redis on the Kubernetes cluster with  the Bitnami charts, but the commands should work on all distributions.

__Changing the cache contents directly on the Redis database can break the consistency of the cache. The supported way to operate with the cache is by using the Cache or the Cache Manager APIs.__

## Accessing the Redis command line interface (redis-cli)

The Redis command line can be accessed with the `redis-cli` command within in the container:

```
kubectl exec -it redis-master-0 -n redis -c redis -- bash
redis-cli
```

Example running the [DBSIZE](https://redis.io/commands/dbsize) command from outside the container:
```
kubectl exec -it redis-master-0 -n redis -c redis -- redis-cli DBSIZE
```
Most Redis commands only apply to the local server. If you are running a cluster, you need to first identify the server that contains the cache.

## HCL Cache objects

The naming of the cache objects follows the convention:  `{cache-<namespace>-<cachename>}-<type>-<id>`

The namespace allows to share Redis for multiple environments, and to distinguish between auth and live. The prefix also contains the name of the cache and it is enclosed with hash tags { }. 
For cluster environments, this ensures all the cache contents are created on the same node. This is a design decision for performance. 

The main two object types are -data (cache contents) and -dep, for dependencies. For example:
```
"{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:depthAndLimit=11,11:UTF-8:requestType=GET"
"{cache-demoqalive-baseCache}-dep-storeId:categoryId:11:10506"
```

### Querying the HCL Cache

The [KEYS](https://redis.io/commands/keys) command can be used to inspect the contents of the Redis cache in a *TEST* environment.
This command should not be used in a live/production environment because it can lock the Redis thread. In production use the 
[SCAN](https://redis.io/commands/scan) command (and its variations) instead as it retrieves data in chunks with a cursor.

The redis-cli interface provides a shortcut to run the SCAN command (--scan) that automatically follows the cursor:

```
I have no name!@redis-master-0:/$ redis-cli --scan --pattern "{cache-demoqalive-baseCache}-*"
"{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=products:catalogId=11501:contractId=-11005:langId=-1:partNumber=BD-BEDS-0002:storeId=11:UTF-8:requestType=GET"
"{cache-demoqalive-baseCache}-dep-WCT+ESINDEX"
"{cache-demoqalive-baseCache}-dep-storeId:partNumber:11:LR-FNTR-0002"
"{cache-demoqalive-baseCache}-dep-storeId:categoryId:11:10506"
"{cache-demoqalive-baseCache}-dep-storeId:partNumber:11:BD-BEDS-0002"
"{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=products:catalogId=11501:langId=-1:partNumber=LR-FNTR-0002:storeId=11:UTF-8:requestType=GET"
"{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:depthAndLimit=11,11:UTF-8:requestType=GET"
..
```

Cache keys (-data) are stored as HASH objects and contain the cached value along with metadata. 

The [HGETALL](https://redis.io/commands/hgetall) command can be used to retrieve the contents:

For example:
```
127.0.0.1:6379> HGETALL "{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:id=10501,10516:UTF-8:requestType=GET"
 1) "created-by"
 2) "demoqalivequery-app-d7ff6c649-ch78j"
 3) "created-at"
 4) "1636061491787"
 5) "dependencies"
 6) "WCT+ESINDEX;;;WCT+FULL_ESINDEX;;;"
 7) "value"
 8) "\x04\x04\t>0com.ibm.ws.cache.servlet.FragmentComposerMemento\x00\x00\x00\x00P\x00 \x02\x00\x00\x00\n>\x0eattributeBytes\x16\x00>\nattributes\x16\x00>\x11characterEncoding\x16\x00>\x13consumeSubfragments \x00>\x0bcontainsESI \x00>\x0bcontentType\x16\x00>\bcontents\x16\x00>\x15externalCacheFragment\x16\x00>\x14externalCacheGroupId\x16\x00>\x0boutputStyle#\x00\x16\x01B\x01\t>4com.ibm.ws.cache.servlet.CacheProxyRequest$Attribute\xdb\x97\x83\x0cL\xc2!\x1d\x00\x00\x00\x02>\x03key\x16\x00>\x05value\x16\x00\x16\x04;\xff>\x15REST_REQUEST_RESOURCE>\x15/api/v2/categories?id\x01\x00\x00\x01B\x03\x16\x04\t>0com.ibm.ws.cache.servlet.DefaultStatusSideEffect\xe2\xe3\xc1\xc89\x19\x01y\x00\x00\x00\x01>\nstatusCode#\x00\x16\x00\x00\x00\xc8\x04\t>)com.ibm.ws.cache.servlet.HeaderSideEffect\x8a\xc4#[9\xfb\xfc=\x00\x00\x00\x03>\x04name\x16\x00>\x03set \x009\xf4\x16\x00\x16>\x0cContent-Type\x00>\x10application/jsonC\a\xaf!{\"contents\":[{\"name\":\"Kitchen\",\"identifier\":\"Kitchen\",\"shortDescription\":\"Create a kitchen that suits your needs and fits your lifestyle\",\"resourceId\":\"https://www.demoqalive.andres.svt.hcl.com/search/resources/api/v2/categories?storeId=11&id=10516&id=10501&contractId=-11005&langId=-1\",\"uniqueID\":\"10516\",\"parentCatalogGroupID\":\"/10516\",\"thumbnail\":\"/hclstore/EmeraldCAS/images/catalog/kitchen/category/dep_kitchen.jpg\",\"seo\":{\"href\":\"/kitchen\"},\"storeID\":\"11\",\"sequence\":\"5.0\",\"fullImage\":\"/hclstore/EmeraldCAS/images/catalog/kitchen/category/dep_kitchen.jpg\",\"id\":\"10516\",\"links\":{\"parent\":{\"href\":\"/search/resources/api/v2/categories?storeId=11&id=-1\"},\"children\":[\"href: /search/resources/api/v2/categories?storeId=11&id=10518\",\"href: /search/resources/api/v2/categories?storeId=11&id=10517\"],\"self\":{\"href\":\"/search/resources/api/v2/categories?storeId=11&id=10516\"}},\"description\":\"Create a kitchen that suits your needs and fits your lifestyle\"},{\"name\":\"Living Room\",\"identifier\":\"LivingRoom\",\"shortDescription\":\"Bring your living space together with comfort and style\",\"resourceId\":\"https://www.demoqalive.andres.svt.hcl.com/search/resources/api/v2/categories?storeId=11&id=10516&id=10501&contractId=-11005&langId=-1\",\"uniqueID\":\"10501\",\"parentCatalogGroupID\":\"/10501\",\"thumbnail\":\"/hclstore/EmeraldCAS/images/catalog/livingroom/category/dep_livingroom.jpg\",\"seo\":{\"href\":\"/living-room\"},\"storeID\":\"11\",\"sequence\":\"1.0\",\"fullImage\":\"/hclstore/EmeraldCAS/images/catalog/livingroom/category/dep_livingroom.jpg\",\"id\":\"10501\",\"links\":{\"parent\":{\"href\":\"/search/resources/api/v2/categories?storeId=11&id=-1\"},\"children\":[\"href: /search/resources/api/v2/categories?storeId=11&id=10503\",\"href: /search/resources/api/v2/categories?storeId=11&id=10502\",\"href: /search/resources/api/v2/categories?storeId=11&id=10504\"],\"self\":{\"href\":\"/search/resources/api/v2/categories?storeId=11&id=10501\"}},\"description\":\"Bring your living space together with comfort and style\"}]}\x01\x01\x00\x00\x00\x01"
 9) "expiry-at"
10) "1636075891787"
```

The [TTL](https://redis.io/commands/ttl) command shows the time-to-live remaining for an entry. When the time expires, the entry is deleted by Redis.

```
127.0.0.1:6379> TTL "{cache-demoqalive-baseCache}-data-/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:id=10501,10516:UTF-8:requestType=GET"
(integer) 13609
```
Dependency information is stored in sets that link to cache-ids. Redis has multiple commands to operate on sets. [SCARD](https://redis.io/commands/scard) shows the size of the set (number of cache ids linked to the dependency id.

```
127.0.0.1:6379> SCARD "{cache-demoqalive-baseCache}-dep-WCT+ESINDEX"
(integer) 9
```
[SMEMBERS](https://redis.io/commands/smembers) lists all the cache-ids for a dependency. This command should only be used for small dependency ids. For dependency ids that can link to a large number of cache-ids,
[SSCAN](https://redis.io/commands/sscan) should be used instead.

```
127.0.0.1:6379> SMEMBERS "{cache-demoqalive-baseCache}-dep-WCT+ESINDEX"
1) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:depthAndLimit=11,11:UTF-8:requestType=GET"
2) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=urls:storeId=11:identifier=tables:langId=-1:UTF-8:requestType=GET"
3) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=urls:storeId=11:identifier=home:langId=-1:UTF-8:requestType=GET"
4) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=urls:storeId=11:identifier=sleepy-head-elegant-queen-bed-bd-beds-0002:langId=-1:UTF-8:requestType=GET"
5) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=products:contractId=-11005:id=14033,14057,14082,14100,14111,14156,14178,14220:langId=-1:storeId=11:UTF-8:requestType=GET"
6) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=store:DC_PathToken_2=11:DC_PathToken_3=sitecontent:DC_PathToken_4=suggestions:catalogId=11501:langId=-1:contractId=-11005:suggestType=Category:UTF-8:requestType=GET"
7) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=categories:storeId=11:langId=-1:contractId=-11005:id=10501,10516:UTF-8:requestType=GET"
8) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=urls:storeId=11:identifier=beds:langId=-1:UTF-8:requestType=GET"
9) "/search/resources/org.springframework.web.servlet.DispatcherServlet.class:DC_Envtype:DC_PathToken_1=api:DC_PathToken_2=v2:DC_PathToken_3=urls:storeId=11:identifier=luncheon-table-dr-tbls-0001:langId=-1:UTF-8:requestType=GET"
```
Dependency IDs do not set an expire, and as per the _volatile-ttl_ memory management rule, they cannot be evicted, as this would result in missing invalidations.

The HCL Cache also maintains other objects such as the cache registry, "{cache_registry-_namespace_}", and "{cache-_namespace_-cachename}-maintenance" which contains information used for maintenance.

#### Deletions
Manually deleting cache objects is not recommended as it can create inconsistencies. The Cache APIs ensure that the metadata and dependencies are correctly updated after an operation.
The [FLUSHALL AYSNC](https://redis.io/commands/flushall) command is often used to clear a Redis database. This clears the Redis cache, but it does not issue the necessary PUBSUB messages for the local caches. 
Use the CacheManager App to issue invalidations and clears.

## Invalidations

The HCL Cache relies on Redis PUBSUB to distribute invalidation messages to the containers to clear local caches.
Each cache defines its own topic for invalidations.

The topic uses the following convention: `{cache-<namespace>-<cachename>}-invalidation`

### PUBSUB command

The [PUBSUB CHANNELS](https://redis.io/commands/pubsub) command lists all the topics with an active subscriber.

```
I have no name!@redis-master-0:/$ redis-cli PUBSUB CHANNELS
  1) "{cache-demoqaauth-services/cache/WCSearchFacetDistributedMapCache}-invalidation"
  5) "{cache-demoqalive-services/cache/WCSearchSTADistributedMapCache}-invalidation"
  6) "{cache-demoqalive-services/cache/SearchContractDistributedMapCache}-invalidation"
  7) "{cache-demoqalive-services/cache/WCCatalogGroupDistributedMapCache}-invalidation"
  8) "{cache-demoqaauth-services/cache/WCCatalogGroupDistributedMapCache}-invalidation"
  9) ...
```

### SUBSCRIBE commmand

The [SUBSCRIBE](https://redis.io/commands/subscribe) and [PSUBSCRIBE](https://redis.io/commands/psubscribe) commands start a topic listener and can be used to monitor invalidations.

This example uses [PSUBSCRIBE](https://redis.io/commands/psubscribe) to subscribe to all live caches. The use of the `--csv` makes the output more readable
```
I have no name!@redis-master-0:/$ redis-cli --csv PSUBSCRIBE "{cache-demoqalive-*}-invalidation"
Reading messages... (press Ctrl-C to quit)
"psubscribe","{cache-demoqalive-*}-invalidation",1
"pmessage","{cache-demoqalive-*}-invalidation","{cache-demoqalive-baseCache}-invalidation","[p:demoqalivecache-app-8597fc98cc-dm2rz]> inv-cache-dep:product:10001"
"pmessage","{cache-demoqalive-*}-invalidation","{cache-demoqalive-baseCache}-invalidation","[p:demoqalivecache-app-8597fc98cc-dm2rz]> inv-cache-dep:product:10002"
```

### PUBLISH commmand

The [PUBLISH](https://redis.io/commands/PUBLISH) command is the counterpart of the SUBSCRIBE command. Although the command is available and could be used to publish invalidation messages,
the supported and recommended way to test invalidations is by using the Cache Manager REST services. This ensures the message format is preserved.
For testing or learning purposes, you can publish invalidations as follows:

```
PUBLISH "{cache-demoqaauth-baseCache}-invalidation" product:10002
PUBLISH "{cache-demoqaauth-baseCache1}-invalidation" inv-cache-clear
```

The Cache APIs add optional metadata information that help identify the source of the invalidations, the time at which they were created and the intended consumers.

## HCL Cache with Redis Clustering

The HCL Cache supports Redis clusters. Thru the use of hash keys, all the objects that belong to the same cache are assigned the same slot. Slots are assigned to unique master servers.

The [CLUSTER KEYSLOT](https://redis.io/commands/cluster-keyslot) command can be used to retrieve the slot for a cache. The hash tags ({ ..}) include both the namespace and the cache name:

```
127.0.0.1:6379> CLUSTER KEYSLOT {cache-demoqalive-baseCache}-data-key1
(integer) 2773
127.0.0.1:6379> CLUSTER KEYSLOT {cache-demoqalive-baseCache}-data-key2
(integer) 2773
127.0.0.1:6379> CLUSTER KEYSLOT {cache-demoqalive-customCache}-data-key1
(integer) 13467
```
The CLUSTER command has a number of options to retrieve information and configure the cluster. The [CLUSTER NODES](https://redis.io/commands/cluster-nodes) command for
example lists node details and their assigned slots. From this list you can see that the baseCache lands on node 10.0.0.3, while the customCache on node 10.0.0.2.

```
127.0.0.1:6379> CLUSTER NODES
04c1fb6be4b726ab9e628a8839caa0dc641988ac 10.0.0.1:6379@16379 master - 0 1636119372578 2 connected 5461-10922
1af0ba43e61824f6c1c16cc0ee66cd3aa58f792b 10.0.0.2:6379@16379 master - 0 1636119373581 3 connected 10923-16383
54a3ebe113c84ea638d3df7706dbdb8ad2ca5836 10.0.0.3:6379@16379 myself,master - 0 1636119373000 1 connected 0-54601
```
You can also use the `kubectl get pods -n redis -o wide` command to map IPs to pods:

```
kubectl get pods -n redis -o wide
NAME                                 READY   STATUS    RESTARTS   AGE   IP           NODE
hcl-commerce-redis-redis-cluster-0   2/2     Running   0          20m   10.0.0.3    gke-perf-cluster-...
hcl-commerce-redis-redis-cluster-1   2/2     Running   0          20m   10.0.0.1    gke-perf-cluster-...
hcl-commerce-redis-redis-cluster-2   2/2     Running   0          20m   10.0.0.2    gke-perf-cluster-...
```
The Cache Manager `/cm/cache/redisNodeInfo` API also displays cache slot and node details.

The HCL Cache can be scaled by adding additional nodes. Redis also allows for slot migration, which means you can select which caches go to which servers.  See the [Cluster Tutorial](https://redis.io/topics/cluster-tutorial) and [Cluster Specification](https://redis.io/topics/cluster-spec) for more details.
