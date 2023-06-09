# HCL Commerce Monitoring - Prometheus and Grafana Integration

HCL Commerce 9.1 has extensive monitoring capabilities based on [Prometheus-style](https://prometheus.io/docs/concepts/metric_types/) metrics. The HCL Commerce pods make metrics available on internal end-points that are consumed by Prometheus thru a process known as scraping.

The popularity of Prometheus and its metrics format has led to broad support, and today you can choose to either install Prometheus and Grafana, or use 3rd-party monitoring applications that can support Prometheus metrics natively.

HCL Commerce also provides a set of Grafana dashboards which are designed to bring attention to critical metrics, highlight problems, and assist you with the resolution of bottlenecks.

Topics:

- [Installing and Configuring Prometheus and Grafana](PrometheusGrafanaInstall.md)
- [HCL Commerce Dashboards dashboards](dashboards/README.md)
- [Third party dashboards](ThirdPartyDashboards.md)
