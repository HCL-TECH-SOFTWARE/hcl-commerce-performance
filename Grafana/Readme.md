# HCL Commerce Monitoring - Prometheus and Grafana Integration

This document describes the HCL Commerce monitoring capabilities with Prometheus and Grafana, and how they provide real-time visibility into the health and performance of the application, to ensure SLAs are met and to aid with the troubleshooting and resolution of bottlenecks.

## HCL Commerce 9.1 Monitoring Architecture

HCL Commerce 9.1 introduced a monitoring framework based on Prometheus-style metrics. The HCL Commerce containers publish endpoints from which metrics can be read. This process is known as scraping. Prometheus discovers the pods to scrape by the use of annotations or ServiceMonitor definitions(CRD). The popularity of Prometheus and its metrics format has led to broad support, and today many 3rd-party monitoring tools can natively consume Prometheus-style metrics.

# HCL Commerce - Grafana Dashboards

In this site you will find a set of Grafana Dashboards for HCL Commerce. These dashboards are designed to bring attention to critical metrics and highlight problems. They give insight into the overall performance, as well as internal components such as caching and backend services. The dashboards can be used in production, or to support the performance tuning process. They are the best way to learn and consume the metrics made available by Commerce. You can use them as-is, or customize to meet your needs. Following is a list of the dashboards currently provided:

### Compatibility:

The provided dashboards are tested with Grafana 7.5.5 and 8.1.4.


#### Transaction and QueryApp servers Dashboard

The _Transaction Servers_ and _QueryApp Servers_ dashboards include a comprehensive set of metrics that give you a detailed view into the performance and health of the servers.
The metrics displayed include:
- Summary: Container Image name; Number of pods (available and unavailable); Requests per second and average response times
- Resources and pools: JVM Heap; CPU Usage; WebContainer/Default Executor pool usage; Datasource usage (tsApp only)
- Logging: Total rate of logging ( messages per second by severity); Rate of warnings and errors, and rate of trace messages, by pod
- REST calls - executions: Total calls per second; Status (Http) per second; Total calls by resource per second, rate and increase
- REST calls - Response times: Average response times by resource; 95 and 99 percentile
- REST calls - Caching: Cache hits and misses per second; Cache hit ratios by resource
- Backend requests (QueryApp only): Active requests by service; Total calls per second per service Average response times, 95, and 99 percentiles

![QueryApp Dashboard](images/query_app.jpg)


#### HCL Cache dashboards

There are currently three dashboards available for _HCL Cache: Remote Cache_, _Local Cache Details_ and _Local Cache Summary_.

*HCL Cache - Remote*:  
Performance statistics for the remote cache, including:
- Availability: Caches in outage mode (from circuit breakers)
- Remote Cache Sizes
- Remote Operations: get/clear/put/invalidate operations per second; error count
- Response Times: Averages; 95 and 99 percentiles
- Hit Ratios
- Invalidation Messages
- Maintenance

![Remote Cache Dashboard](images/hcl_cache_remote.jpg)

*Local Cache Summary*:
Single table per pod listing all caches and including sizes and footprint

*Local Cache Details*:
Detailed information for local caches including sizes in entries and footprint; hit ratios; operations and removals per second

## 3rd-party Grafana Dashboards

When using the Kube-prometheus-stack chart, Grafana is pre-configured with a number of dashboards for monitoring of Kubernetes, including nodes, pods and workloads. 
Besides installing the HCL Commerce dashboards, most of the stack used by Commerce makes their own dashboards available. The [Grafana](https://grafana.com/grafana/dashboards) website is a good source for finding additional dashboards.

Some of the 3rd-party dashboard you might want to configure include:
- [Nginx Ingress](https://github.com/kubernetes/ingress-nginx/tree/main/deploy/grafana/dashboards)
- [Redis](https://grafana.com/grafana/dashboards/11835)
- [NiFi](https://grafana.com/grafana/dashboards/12375) (Only with ServiceMonitors)
- [Zookeeper](https://grafana.com/grafana/dashboards/10465)
