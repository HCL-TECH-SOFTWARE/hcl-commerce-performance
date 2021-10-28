# Prometheus and Grafana Install

To take advantage of the HCL Commerce native monitoring capabilities, a Prometheus-compatible monitoring system must be installed. If you are not consuming metrics with the Cloud's native monitoring framework or a 3rd-party system, you can install Prometheus Operator on the Kubernetes cluster. 

### Kube-prometheus-stack

Kube-prometheus-stack is the most popular and recommended option for installing Prometheus. It's an all-in-one install that includes Prometheus Operator (ServiceMonitor support), Grafana, and pre-configured instrumentations for Kubernetes monitoring.

https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install [RELEASE_NAME] prometheus-community/kube-prometheus-stack
```
##### ServiceMonitor selectors

With the default configuration, service monitors defined by HCL Commerce are not picked up by Prometheus. This is because Prometheus only loads service monitors
with a particular label (e.g. release: prometheus) or in a determined namespace. You can change this configuration during install with the options _serviceMonitorSelectorNilUsesHelmValues_
and _serviceMonitorSelector_:

```
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    serviceMonitorSelector: {}
```

After installation, you can verify this configuration by inspecting the _prometheus_ resource:

```
kubectl edit prometheus -n monitoring
```

```
  serviceMonitorNamespaceSelector: {}
  serviceMonitorSelector: {}
```
For more details see the [troubleshooting](Troubleshooting.md) document.

### Prometheus

The following distribution installs Prometheus only. This option lacks ServiceMonitor CRD support. As ServiceMonitors are not defined, HCL Commerce must be installed with the _prometheusAnnotations_ option.
Grafana must be installed separately.

https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install [RELEASE_NAME] prometheus-community/prometheus
```
## Commerce Dashboards installation

Once Prometheus and Grafana are installed, you can import the HCL Commerce Grafana dashboards. Although it's possible to import the dashboards individually using the json 
file, the hc-dashboards chart can assist you in installing all the dashboards at once. See the [dashboards](dashboards) page for more information.
