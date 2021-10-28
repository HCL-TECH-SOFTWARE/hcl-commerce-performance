# HCL Commerce Monitoring - Prometheus and Grafana Integration

This document describes the HCL Commerce monitoring capabilities with Prometheus and Grafana, and how they provide real-time visibility into the health and performance of the application, to ensure SLAs are met and to aid with the troubleshooting and resolution of bottlenecks.

## HCL Commerce 9.1 Monitoring Architecture

HCL Commerce 9.1 introduced a monitoring framework based on Prometheus-style metrics. The HCL Commerce containers publish endpoints from which metrics can be read. This process is known as scraping. Prometheus discovers the pods to scrape by the use of annotations or ServiceMonitor definitions(CRD). The popularity of Prometheus and its metrics format has led to broad support, and today many 3rd-party monitoring tools can natively consume Prometheus-style metrics.

