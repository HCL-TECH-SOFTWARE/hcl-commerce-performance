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

See [Kube-prometheus-stack-step-by-step](Kube-prometheus-stack-step-by-step.md) for additional details.

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

## HCL Commerce - Metrics Enablement

The HCL Commerce chart provides options for enabling integration with Prometheus. Although _metrics_ are enabled by default, the _serviceMonitor_ or  _prometheusAnnotations_ option must be enabled to match your Prometheus install. 

```
## Flag to enable metrics. Enabled by default
metrics:
  enabled: true
  ## Flag to add prometheus scraping annotations to pods. Disabled by default
  prometheusAnnotations:
    enabled: false
  ## Flag to enable service monitor. Disabled by default    
  serviceMonitor:
    enabled: false
    ## Specify a namespace in which to install the ServiceMonitor resource.
    ## Default to use the same release namespace where commerce is deployed to
    # namespace: monitoring
    # interval between service monitoring requests
    interval: 15s
    ## Defaults to what's used if you follow CoreOS [Prometheus Install Instructions](https://github.com/helm/charts/tree/master/stable/prometheus-operator#tldr)
    ## [Prometheus Selector Label](https://github.com/helm/charts/tree/master/stable/prometheus-operator#prometheus-operator-1)
    ## [Kube Prometheus Selector Label](https://github.com/helm/charts/tree/master/stable/prometheus-operator#exporters)
    selector:
      prometheus: kube-prometheus
```

If your Prometheus distribution supports ServiceMonitor CRDs, such as Kube-prometheus-stack, configure _metrics.serviceMonitor.enabled=true_. This is the recommended option.

ServiceMonitors instruct Prometheus Operator what Commerce services to scrape, including details such as the path and the frequency. Prometheus Operator must be installed before using this option, as otherwise Kubernetes will not recognize the ServiceMonitor CRD and the Commerce installation will fail.

```
kubectl describe servicemonitor demoqaingest-app -n commerce
...
Spec:
  Endpoints:
    Interval:  15s
    Path:      /monitor/metrics
    Port:      metrics
  Namespace Selector:
    Match Names:
      commerce
  Selector:
    Match Labels:
      Component:  demoqaingest-app
```

The _prometheusAnnotations_ option is available since HCL Commerce 9.1.8. It is available when Prometheus Operator (and ServiceMonitors) are not used. When enabled, it adds
prometheus scrape annotations to the pods as follows:

```
  prometheus.io/scrape: "true"
  prometheus.io/path: /monitor/metrics
  prometheus.io/port: "8280"
```

Note: The NiFi pod exports two metrics endpoints. One with HCL Commerce metrics, such as for caching, and one native to NiFi (PrometheusReportingTask). When annotations are used, only the HCL Commerce metrics endpoint is exported.


## Commerce Dashboards installation

Once Prometheus and Grafana are installed, you can import the HCL Commerce Grafana dashboards. Although it's possible to import the dashboards individually using the json 
file, the hc-dashboards chart can assist you in installing all the dashboards at once. See the [dashboards](dashboards) page for more information.

## Troubleshooting

See the [troubleshooting](Troubleshooting.md) document.
