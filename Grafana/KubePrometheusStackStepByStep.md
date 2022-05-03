# kube-prometheus-stack - Step by Step Instructions

This page includes sample instructions for installing [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack).

1. Create the namespace - In this case we use *monitoring* for the namespace.
``` 
kubectl create ns monitoring
```
2. Add and update the repository
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
3. Review the sample values.yaml provided. Persistence is required for both Prometheus and Grafana
```
grafana:
  plugins:
  - redis-datasource
  persistence:
    type: pvc
    enabled: true
    storageClassName: standard
    accessModes:
      - ReadWriteOnce
    size: 15Mi
    finalizers:
      - kubernetes.io/pvc-protection
prometheus:
  prometheusSpec:
    # With below two lines service monitors defined by commerce will be picked up
    serviceMonitorSelectorNilUsesHelmValues: false
    serviceMonitorSelector: {}
    storageSpec:
      volumeClaimTemplate:
        spec:
          # Name of the PV you created beforehand
          #volumeName: prometheus-pv
          accessModes: ["ReadWriteOnce"]
          # StorageClass should match your existing PV's storage class
          storageClassName: standard
          resources:
            requests:
              storage: 50Gi
```
3.  Install Prometheus and Grafana using below values.yaml
```
helm install prometheus prometheus-community/kube-prometheus-stack -f values.yaml -n monitoring
```
4. Wait for the containers to be in ready state
```
kubectl get pods -n monitoring 
NAME                                                     READY   STATUS    RESTARTS   
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          
prometheus-grafana-d4f579f8d-t5h6d                       2/2     Running   0          
prometheus-kube-prometheus-operator-586bdcb8d7-7p6bc     1/1     Running   0         
prometheus-kube-state-metrics-84dfc44b69-8nncd           1/1     Running   0          
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          
prometheus-prometheus-node-exporter-7wl42                1/1     Running   0          
prometheus-prometheus-node-exporter-cwjhk                1/1     Running   0          
prometheus-prometheus-node-exporter-dls2k                1/1     Running   0          
prometheus-prometheus-node-exporter-lbfdp                1/1     Running   0          
prometheus-prometheus-node-exporter-x9rrn                1/1     Running   0          

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



