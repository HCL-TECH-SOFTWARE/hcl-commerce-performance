# HCL Cache Utilities

The HCL Cache Manager pod includes the following utilities:

- [hcl-cache-benchmark](#hcl-cache-benchmark)
- [hcl-cache-rdb](#hcl-cache-rdb)
- [hcl-cache-node](#hcl-cache-node)

## hcl-cache-benchmark

The hcl-cache-benchmark utility enables you to benchmark HCL Cache operations such as Put, Get, Invalidate and Clear. This utility gives you a reference for how long each operation takes from the client. The performance of the client, network and Redis server will impact the results.

As there is a network round-trip with each cache operation, the numbers reported represent average responses from the client's perspective, and not the limits
of the Redis server. For reference, cache operations such as Gets and Puts should take about a millisecond. The performance of clear and invalidation operations
will vary depending on the amount of data in the Redis server and the amount of data being cleared.

When using this tool in a production environment, consider that it can have an impact on the system. Also, depending on the configuration used for number of keys and payload size, the Redis server's memory could be full. By default, the tool will attempt to insert 50,000 keys each with a 2k footprint, leading to a temporary use of Redis memory of up to 100mb.

When working on clustered environments, only one server will be tested. The default cache (RemoteOnlyCache1) is mapped to slot 3205. Other nodes can be used by switching the cache name as follows:

```
   3205 {cache-benchmark-services/cache/benchmark/RemoteOnlyCache1}
  15590 {cache-benchmark-services/cache/benchmark/RemoteOnlyCache2}
  11463 {cache-benchmark-services/cache/benchmark/RemoteOnlyCache3}
   7200 {cache-benchmark-services/cache/benchmark/RemoteOnlyCache4}
```

### Usage

```
usage: java -jar hcl-cache-benchmark
   -c,--cache <Cache Name>        Cache name. Defaults to
                                  services/cache/benchmark/RemoteOnlyCache1
                                  under benchmark namespace
   -h,--help                      Prints this usage information
   -k,--keys <Number of Keys>     Number of keys to insert. Defaults to 50000
   -y,--noprompt                  Do not show the warning and prompt for
                                  confirmation before starting the benchmark
   -z,--size <Value Size>         Value size. Defaults to 2048 bytes
```

### Sample reports

The following sample reports were obtained from HCL Commerce test environments in GCP and Azure. The `hcl-cache-benchmark` utility is single threaded
so the reports do not indicate total capacity limits, but provide a reference point for comparison.

> The average time for *Get* and *Put* operations should ideally be under 1 ms.

#### GCP - Bitnami install on local Kubernetes cluster using e2-custom-4-32768 (Intel Skylake CPU)

```
---------------------------------------------   -------------------------------------------------
| Operation       | Executions | Time (sec) |   | Mean (ms) | 90p (ms)  | 95p (ms)  | 99p (ms)  |
---------------------------------------------   -------------------------------------------------
| put             |     50,000 |      19.08 |   |     0.382 |     0.463 |     0.514 |     0.715 |
| get             |     50,000 |      12.68 |   |     0.254 |     0.326 |     0.354 |     0.427 |
| invalidate      |     25,000 |       7.35 |   |     0.294 |     0.376 |     0.402 |     0.452 |
| clear           |          1 |       0.51 |   |   510.711 |   510.657 |   510.657 |   510.657 |
---------------------------------------------   -------------------------------------------------
```

#### Azure - Bitnami install on local Kubernetes cluster using Standard_F4s_v2 

```
---------------------------------------------   -------------------------------------------------
| Operation       | Executions | Time (sec) |   | Mean (ms) | 90p (ms)  | 95p (ms)  | 99p (ms)  |
---------------------------------------------   -------------------------------------------------
| put             |     50,000 |      30.92 |   |     0.618 |     0.741 |     0.793 |     0.934 |
| get             |     50,000 |      26.97 |   |     0.539 |     0.622 |     0.659 |     0.764 |
| invalidate      |     25,000 |      13.92 |   |     0.557 |     0.661 |     0.694 |     0.803 |
| clear           |          1 |       0.49 |   |   487.550 |   487.326 |   487.326 |   487.326 |
---------------------------------------------   -------------------------------------------------
```

#### Azure - Bitnami install on local Kubernetes cluster using Standard_E8-4s_v5

```
---------------------------------------------   -------------------------------------------------
| Operation       | Executions | Time (sec) |   | Mean (ms) | 90p (ms)  | 95p (ms)  | 99p (ms)  |
---------------------------------------------   -------------------------------------------------
| put             |     50,000 |      11.58 |   |     0.232 |     0.279 |     0.324 |     0.469 |
| get             |     50,000 |       8.47 |   |     0.169 |     0.200 |     0.222 |     0.289 |
| invalidate      |     25,000 |       4.03 |   |     0.161 |     0.190 |     0.205 |     0.244 |
| clear           |          1 |       0.41 |   |   412.680 |   412.615 |   412.615 |   412.615 |
---------------------------------------------   -------------------------------------------------
```

## hcl-cache-rdb

The hcl-cache-rdb utility consumes a Redis RDB file. RDB files are point-in-time
snapshots of the Redis memory contents, and are used for replication and failover.
See this link for more information: https://redis.io/topics/persistence

The utility parses the contents of a Redis RDB file and generates a report that
is useful for tuning and troubleshooting.

The information in the report include:
- List of caches found, with number of entries and estimated size in MB (footprint)
- Histogram analysis of:
  * Cache entry footprints (size in bytes)
  * Time to expiry
  * Idle time
- Top cache entries by size
- Top dependencies by Size

> Due to library limitations, this utility does not currently support Redis 7 (version 10) RDB files.

### Obtaining an RDB file

If your Redis server is already configured with RDB persistence (CONFIG SAVE GET),
RDB files are already generated at the configured intervals. The dump.rdb file can
be found under the /data directory in the container.

You can also request RDB files on demand by using the SAVE and BGSAVE commands.

The SAVE command is synchronous. Because file generation can take a few seconds, the Redis server
might become unavailable or be restarted.

The BGSAVE command is asynchronous and does not
block the Redis server. The Redis log (kubectl logs) will include information for when
background saves are started and completed:

```
1:M 23 Jun 2021 14:23:31.568 * Background saving started by pid 3763
3763:C 23 Jun 2021 14:23:32.921 * DB saved on disk
3763:C 23 Jun 2021 14:23:32.926 * RDB: 5 MB of memory used by copy-on-write
1:M 23 Jun 2021 14:23:33.001 * Background saving terminated with success
```

### Running the hcl-cache-rdb utility

The utility can be started by using the hcl-cache-rdb.sh script. An error will be displayed if the RDB file is not found.

The size of the heap available to the utility is constrained by the container limits. The available size is printed during startup: (e.g. INFO: -Xmx 1536mb).

When parsing large RDB files, it is possible that the utility fails with OutOfMemory error. In that case you can increase the size of the container, manually specify a new -Xmx limit, or copy the utility to a separate environment that can run Java +8.

Running the utility on a separate environment is also recommended to avoid having to copy the RDB files into the container.

### Usage
```
usage: java -jar rdbparser.jar [options]
 -c,--cache <arg>       Cache name. Defaults to all
 -f,--file <arg>        RDB file. Defaults to dump.rdb in current
                        directory
 -h,--help              Prints this help
 -k,--key <arg>         Dumps keys that contain the parameter. In this
                        mode the report is not shown
 -n,--namespace <arg>   Namespace. Defaults to all
```

## hcl-cache-node

With Redis Cluster, caches are assigned to particular nodes. The slot assigment is determined using the namespace and the cache name: {cache-NAMESPACE-CACHENAME}.
This utility can be used for planning as it helps preview how a list of caches is assigned on a given number of Redis nodes.

The slot for a cache can also be determined using the CLUSTER KEYSLOT command.

The Cache Manager App provided the "/cache/redisNodeInfo" REST interface that provides node and cache mapping for a running environment. This mapping is also displayed in the "HCL Cache - Remote" Grafana dashboard.

### Usage Info
``` 
usage: java -jar cache_node.jar [options]
This utility can help you plan which node an HCL Cache will be assigned
to.
 -c,--cache-list <arg>    Comma separated list of caches.
 -f,--cache-file <arg>    File containing list of caches. Defaults to
                          cacheList.txt in current directory.
 -h,--help                Prints this help.
 -n,--namespaces <arg>    Comma separated list of namespaces, defaults to
                          [demoqaauth, demoqalive].
 -r,--redis-nodes <arg>   Number of Redis nodes (3-10). Defaults to 3.
```

Licensed Materials - Property of HCL Technologies Limited.
(C) Copyright HCL Technologies Limited 2022

