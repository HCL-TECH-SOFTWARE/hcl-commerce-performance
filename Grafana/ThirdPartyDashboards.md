# Stack Monitoring and Third-party dashboards


## Elasticsearch Exporter

- [Elasticsearch Exporter](https://github.com/prometheus-community/elasticsearch_exporter)
- [Helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-elasticsearch-exporter)

### Installation

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install esexporter -n elastic prometheus-community/prometheus-elasticsearch-exporter --set es.uri="http://hcl-commerce-elasticsearch:9200" --set serviceMonitor.enabled=true --set serviceMonitor.interval=20s
```

The default interval is updated from 10s to 20s. The exporter fetches information from an Elasticsearch cluster on every scrape, therefore having a too short scrape interval can impose load on ES master nodes, particularly if you run with --es.all and --es.indices.

### Grafana Dashboard:
- [Elasticsearch Exporter Quickstart and Dashboard](https://grafana.com/grafana/dashboards/14191-elasticsearch-overview/)


## Redis

Metrics and service-monitors must be enabled when installing [Redis](https://github.com/bitnami/charts/tree/main/bitnami/redis#metrics-parameters).

### Grafana Dashboard:
- [Redis Dashboard for Prometheus Redis Exporter (helm stable/redis-ha)](https://grafana.com/grafana/dashboards/11835-redis-dashboard-for-prometheus-redis-exporter-helm-stable-redis-ha/)










