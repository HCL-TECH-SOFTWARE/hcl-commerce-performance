# kube-prometheus-stack - Step by Step Instructions

This page includes sample instructions for installing [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack).

1. Add and update the Helm repository
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
2. Review the sample values.yaml provided. Change as required
```
# GKE Only
prometheusOperator:
  admissionWebhooks:
    failurePolicy: Ignore

grafana:
  # Update
  adminPassword: prom-operator
  persistence:
    type: pvc
    enabled: true
    accessModes:
      - ReadWriteOnce
    size: 1Gi
    finalizers:
      - kubernetes.io/pvc-protection

prometheus:
  prometheusSpec:
    retention: 365d
    scrapeInterval: 30s
    evaluationInterval: 30s
    serviceMonitorSelectorNilUsesHelmValues: false
    serviceMonitorSelector: {}
    scrapeClasses:
    - default: true
      name: default
	  fallbackScrapeProtocol: PrometheusText0.0.4
    enableRemoteWriteReceiver: true
    resources:
      limits:
        cpu: "3"
        memory: 4096Mi
      requests:
        cpu: "2"
        memory: 4096Mi
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 150Gi
```
3. Install with helm:
```
helm install prometheus prometheus-community/kube-prometheus-stack --create-namespace -f values.yaml -n metrics
```

## Accessing the Prometheus and Grafana consoles

Although both, the Prometheus and Grafana's charts provide options for ingress rules, ingress is not defined in the sample provided.
You can use *port-forwarding* to the service to access each console.

```
kubectl port-forward -n monitoring service/prometheus-kube-prometheus-prometheus 9090:9090
```
```
kubectl port-forward -n monitoring service/prometheus-grafana 80:80
```

Consoles can the be accessed thru http://localhost:9090 and http://localhost. The first port in the _port-forward_ rule is the local port and it can be changed.

The _port-forward_ approach requires _kubectl_ to be available in the local machine. If _kubectl_ is installed on a different machine, you can use _putty_ for
additional port forwarding.
