# HCL Commerce Grafana Dashboards

Grafana dashboards can be installed individually by importing the .json files into the Grafana UI,
or using this Helm chart to define them all at once. 

This Helm chart loads each dashboard Json file into a Config Map on the specified namespace. 
Grafana automatically finds and loads the dashboards from the Config Map that have the
specified label (grafana_dashboard). By default Grafana only looks for Config Maps on its
own namespace, but it can be configured to search in all. 

## Installation

The following steps download the git repo and install the dashboards using the monitoring 
namespace (on which Grafana is install in this system)

```
git clone https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-performance.git
helm install hc-dashboards ./hcl-commerce-performance/Grafana/dashboards -n monitoring --set folder=dashboards/prometheus-operator
```

* Use --set folder=dashboards/prometheus if your Prometheus version is not Operator

If `git` is not installed, the repo can be downloaded with `curl` or `wget` as follows. Notice the
directory name will change.

```
curl -k -J -L -O https://github.com/HCL-TECH-SOFTWARE/hcl-commerce-performance/archive/main.zip 
```

The `get configmap` command can be used to verify that the dashboards were loaded 
corrected:

```
kubectl get configmap -n monitoring | grep hcl-commerce
hcl-commerce-grafana-cache-local-details                       1      2m8s
hcl-commerce-grafana-cache-local-summary                       1      2m8s
hcl-commerce-grafana-cache-remote                              1      2m8s
hcl-commerce-grafana-crs-performance                           1      2m8s
hcl-commerce-grafana-ingest-performance                        1      2m8s
hcl-commerce-grafana-java-details                              1      2m8s
hcl-commerce-grafana-java-summary                              1      2m8s
hcl-commerce-grafana-query-app                                 1      2m8s
```

### Troubleshooting:

It might take a few seconds for the dashboards to appear in the Grafana UI. 
If the dashboard do not appear, verify that your Grafana installation enabled
the sidecar/dashboards options.

If the sidecar is enabled, it's possible that the dashboards were loaded into
an namespace that Grafana does not consider, or that the label was changed.

