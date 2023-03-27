# Change Log

## HCL Commerce 9.1.12

- *Improvement*: HC-20121 - New timer for cached JPA operations: access_bean_cache and updated Transaction Servers dashboard
- *Improvement*: HC-20573 - New timer (request_store) and counter (request_store_status_total) for Web request time. Updated Transaction Servers for local store and CRS dashboard
- *Improvement*: All existing dashboards have been updated with incremental improvements

#### Notes:
- Starting in 9.1.12, only the Prometheus-operator version of the dashboards is maintained. Updates might be required for use with other versions of prometheus
- Dashboards are tested with Grafana 8.5. This, or a higher version is required for use

## HCL Commerce 9.1.11

- *Improvement*: HC-16663 - Implement new Solr Search dashboard and metrics for Solr processors and backend requests
