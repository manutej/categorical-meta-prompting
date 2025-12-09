# Kubernetes Self-Healing Spark Data Pipeline

A production-ready Kubernetes architecture for deploying Apache Spark streaming applications with comprehensive self-healing capabilities, auto-scaling, monitoring, and disaster recovery.

## Architecture Overview

This deployment architecture implements:

- **Self-Healing**: Automatic pod restarts, health checks, checkpointing
- **Auto-Scaling**: HPA/VPA for executors based on CPU, memory, and custom metrics
- **High Availability**: Multi-replica operator, pod anti-affinity, disruption budgets
- **Security**: RBAC, network policies, secret encryption, pod security standards
- **Monitoring**: Prometheus metrics, Grafana dashboards, alerting rules
- **Disaster Recovery**: Checkpoint backups, volume snapshots, multi-region support

## Resource Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ NAMESPACE: spark-pipeline                                            │   │
│  │ (ResourceQuota, LimitRange, NetworkPolicy)                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│         ┌──────────────────────────┼──────────────────────────┐              │
│         │                          │                          │              │
│         ▼                          ▼                          ▼              │
│  ┌─────────────┐          ┌──────────────┐          ┌──────────────┐       │
│  │   RBAC      │          │   STORAGE    │          │   NETWORK    │       │
│  ├─────────────┤          ├──────────────┤          ├──────────────┤       │
│  │ • SA: spark-│          │ • StorageClass│         │ • Services   │       │
│  │   operator  │          │   (SSD)       │         │   - Headless │       │
│  │ • SA: spark │          │ • PVC:        │         │   - UI       │       │
│  │ • ClusterRole│         │   checkpoint  │         │   - History  │       │
│  │ • Role      │          │ • PVC:        │         │ • Ingress    │       │
│  │ • Bindings  │          │   eventlog    │         │   - UI       │       │
│  └─────────────┘          │ • ConfigMap:  │         │   - History  │       │
│         │                 │   s3-config   │         │ • NetworkPol │       │
│         │                 │ • Secret:     │         │   - Driver   │       │
│         │                 │   s3-creds    │         │   - Executor │       │
│         │                 │ • ConfigMap:  │         │   - S3 Egress│       │
│         │                 │   spark-      │         └──────────────┘       │
│         │                 │   defaults    │                 │              │
│         │                 └──────────────┘                  │              │
│         │                         │                         │              │
│         └─────────────────────────┼─────────────────────────┘              │
│                                   │                                         │
│                                   ▼                                         │
│         ┌────────────────────────────────────────────────────┐             │
│         │        SPARK OPERATOR (Deployment)                 │             │
│         │        - Replicas: 2 (HA)                          │             │
│         │        - Webhook enabled                           │             │
│         │        - Metrics exposed                           │             │
│         │        - Leader election                           │             │
│         └────────────────────────────────────────────────────┘             │
│                                   │                                         │
│                                   │ Manages                                 │
│                                   ▼                                         │
│         ┌────────────────────────────────────────────────────┐             │
│         │    SPARKAPPLICATION CRD                            │             │
│         │    - Type: Streaming (Python)                      │             │
│         │    - RestartPolicy: OnFailure (5 retries)          │             │
│         │    - Driver: 2 cores, 4GB RAM                      │             │
│         │    - Executor: 2 cores, 8GB RAM (5 instances)      │             │
│         │    - Checkpointing enabled                         │             │
│         │    - Volumes: checkpoint, eventlog                 │             │
│         └────────────────────────────────────────────────────┘             │
│                         │                  │                                │
│           ┌─────────────┴──────┐    ┌──────┴───────────┐                  │
│           ▼                    ▼    ▼                  ▼                   │
│  ┌──────────────┐      ┌─────────────────┐    ┌──────────────┐           │
│  │ DRIVER POD   │      │ EXECUTOR PODS   │    │ HISTORY SVR  │           │
│  ├──────────────┤      ├─────────────────┤    ├──────────────┤           │
│  │ • Liveness   │      │ • HPA/VPA       │    │ • Deployment │           │
│  │   Probe      │      │ • Anti-affinity │    │ • Service    │           │
│  │ • Readiness  │      │ • Spot tolerant │    │ • PVC mount  │           │
│  │   Probe      │      │ • PDB (min: 2)  │    └──────────────┘           │
│  │ • PDB (min:1)│      │ • Metrics       │             │                  │
│  │ • Metrics    │      │   exposed       │             │                  │
│  │ • On-demand  │      └─────────────────┘             │                  │
│  │   node       │               │                      │                  │
│  └──────────────┘               │                      │                  │
│         │                       │                      │                  │
│         └───────────────────────┴──────────────────────┘                  │
│                                 │                                          │
│                                 ▼                                          │
│         ┌────────────────────────────────────────────────────┐            │
│         │         MONITORING & ALERTING                      │            │
│         ├────────────────────────────────────────────────────┤            │
│         │ • ServiceMonitor (Prometheus scraping)             │            │
│         │ • PrometheusRule (Alerts)                          │            │
│         │   - Driver down                                    │            │
│         │   - High executor failure rate                     │            │
│         │   - Streaming delay                                │            │
│         │   - Memory pressure                                │            │
│         │   - Checkpoint failures                            │            │
│         │ • Grafana Dashboard                                │            │
│         │ • Recording Rules (aggregations)                   │            │
│         └────────────────────────────────────────────────────┘            │
│                                                                             │
│         ┌────────────────────────────────────────────────────┐            │
│         │         DISASTER RECOVERY                          │            │
│         ├────────────────────────────────────────────────────┤            │
│         │ • CronJob: Checkpoint backup (every 6h)            │            │
│         │ • CronJob: Event log archival (daily)              │            │
│         │ • CronJob: Volume snapshots (every 12h)            │            │
│         │ • Job: Checkpoint restore (manual)                 │            │
│         │ • Velero Schedule (cluster backup)                 │            │
│         │ • RTO: 15 minutes, RPO: 6 hours                    │            │
│         └────────────────────────────────────────────────────┘            │
│                                                                             │
│         ┌────────────────────────────────────────────────────┐            │
│         │         SECURITY                                   │            │
│         ├────────────────────────────────────────────────────┤            │
│         │ • PodSecurityPolicy / Pod Security Standards       │            │
│         │ • NetworkPolicy (least privilege)                  │            │
│         │ • Secret encryption (KMS)                          │            │
│         │ • TLS/SSL for Spark UI & RPC                       │            │
│         │ • RBAC (least privilege)                           │            │
│         │ • OPA Gatekeeper (policy enforcement)              │            │
│         │ • External Secrets Operator (vault integration)    │            │
│         └────────────────────────────────────────────────────┘            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   EXTERNAL DEPENDENCIES       │
                    ├───────────────────────────────┤
                    │ • S3/MinIO (data lake)        │
                    │ • Kafka (optional streaming)  │
                    │ • Prometheus (metrics)        │
                    │ • Grafana (visualization)     │
                    │ • Cert-Manager (TLS certs)    │
                    │ • AWS Secrets Manager (creds) │
                    └───────────────────────────────┘
```

## Component Dependencies

### Deployment Order

1. **Namespace & RBAC** (`01-namespace.yaml`, `02-rbac.yaml`)
   - Namespace isolation
   - Service accounts, roles, role bindings

2. **Storage** (`03-storage.yaml`)
   - StorageClass for SSD-backed volumes
   - PVCs for checkpoints and event logs
   - ConfigMaps for S3 and Spark configuration
   - Secrets for S3 credentials

3. **Spark Operator** (`04-spark-operator-helm-values.yaml`)
   - Helm chart deployment
   - Webhook configuration
   - Leader election for HA

4. **SparkApplication** (`05-spark-application.yaml`)
   - Main Spark streaming job definition
   - Driver and executor configuration
   - Self-healing policies (restart, probes)

5. **Auto-Scaling** (`06-autoscaling.yaml`)
   - HPA for executors
   - VPA for resource optimization
   - PodDisruptionBudgets
   - PriorityClasses

6. **Networking** (`07-networking.yaml`)
   - Services (headless, UI, history server)
   - Ingress for external access
   - NetworkPolicies for security

7. **Monitoring** (`08-monitoring.yaml`)
   - ServiceMonitors for Prometheus
   - PrometheusRules for alerting
   - Grafana dashboards

8. **Security** (`09-security.yaml`)
   - PodSecurityPolicy / Standards
   - TLS certificates
   - Admission webhooks

9. **Disaster Recovery** (`10-disaster-recovery.yaml`)
   - Backup CronJobs
   - Volume snapshots
   - Restore jobs

## Self-Healing Features

### 1. Automatic Restart on Failure

**Location**: `05-spark-application.yaml`

```yaml
restartPolicy:
  type: OnFailure
  onFailureRetries: 5
  onFailureRetryInterval: 30  # seconds
```

- **How it works**: Operator automatically restarts failed driver pods up to 5 times
- **Trigger**: Pod exit code != 0
- **Recovery time**: 30 seconds + pod startup time

### 2. Health Probes

**Location**: `05-spark-application.yaml`

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 4040
  initialDelaySeconds: 60
  periodSeconds: 30
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 4040
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

- **Liveness**: Restarts pod if unresponsive for 90s (3 failures × 30s)
- **Readiness**: Removes pod from service endpoints if not ready

### 3. Checkpoint-Based Recovery

**Location**: `05-spark-application.yaml`, `03-storage.yaml`

```yaml
volumes:
  - name: checkpoint-storage
    persistentVolumeClaim:
      claimName: spark-checkpoint-pvc

sparkConf:
  "spark.streaming.receiver.writeAheadLog.enable": "true"
```

- **How it works**: Streaming state persisted to PVC, restored on restart
- **RPO**: Last checkpoint interval (10 seconds)
- **Storage**: SSD-backed PVC with ReadWriteMany access

### 4. Auto-Scaling Executors

**Location**: `06-autoscaling.yaml`

```yaml
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: spark_streaming_processing_rate
```

- **Scale-up**: Add executors when CPU > 70% or processing rate high
- **Scale-down**: Remove executors conservatively (10% every 60s)
- **Self-healing**: Automatically adds capacity during load spikes

### 5. Pod Disruption Budgets

**Location**: `06-autoscaling.yaml`

```yaml
spec:
  minAvailable: 2  # For executors
  minAvailable: 1  # For driver
```

- **Protection**: Prevents voluntary disruptions (node drain, upgrades)
- **Ensures**: Minimum executors always available

### 6. Monitoring & Alerting

**Location**: `08-monitoring.yaml`

Critical alerts:
- `SparkDriverDown`: Driver pod unresponsive > 2min
- `HighExecutorFailureRate`: Executor failures > 0.1/sec
- `HighStreamingDelay`: Processing delay > 30s
- `CheckpointFailure`: Checkpoint write failed

- **Self-healing trigger**: Alerts can trigger automated remediation via alertmanager webhooks

### 7. Disaster Recovery

**Location**: `10-disaster-recovery.yaml`

- **Checkpoint backups**: Every 6 hours to S3
- **Volume snapshots**: Every 12 hours
- **Retention**: 7 days
- **RTO**: 15 minutes (restore + restart)
- **RPO**: 6 hours (backup frequency)

## Key Configuration Files

| File | Purpose | Key Self-Healing Features |
|------|---------|---------------------------|
| `01-namespace.yaml` | Namespace isolation | ResourceQuota prevents resource exhaustion |
| `02-rbac.yaml` | Security permissions | Least-privilege access control |
| `03-storage.yaml` | Persistent storage | SSD-backed checkpoints for fast recovery |
| `04-spark-operator-helm-values.yaml` | Operator deployment | HA with 2 replicas, leader election |
| `05-spark-application.yaml` | Main Spark job | Restart policy, probes, checkpointing |
| `06-autoscaling.yaml` | Dynamic scaling | HPA/VPA, PDB, priority classes |
| `07-networking.yaml` | Network configuration | NetworkPolicies, service redundancy |
| `08-monitoring.yaml` | Observability | Alerts for failures, metrics scraping |
| `09-security.yaml` | Security hardening | Pod security, TLS, network segmentation |
| `10-disaster-recovery.yaml` | Backup/restore | Automated backups, restore procedures |

## Prerequisites

1. **Kubernetes Cluster**: v1.23+ with CSI driver support
2. **Helm**: v3.x for operator installation
3. **Storage**: CSI driver with ReadWriteMany support (EFS, NFS, Ceph)
4. **Operators** (optional but recommended):
   - Prometheus Operator (monitoring)
   - Cert-Manager (TLS certificates)
   - External Secrets Operator (secret management)
   - Velero (cluster backups)
   - KEDA (event-driven autoscaling)

## Deployment Instructions

### Step 1: Install Prerequisites

```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Install Cert-Manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set installCRDs=true

# Install Metrics Server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Step 2: Deploy Namespace & RBAC

```bash
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-rbac.yaml
```

### Step 3: Configure Storage

```bash
# Update S3 credentials in 03-storage.yaml (or use External Secrets)
kubectl apply -f 03-storage.yaml

# Verify PVCs are bound
kubectl get pvc -n spark-pipeline
```

### Step 4: Install Spark Operator

```bash
# Add Spark Operator Helm repository
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update

# Install operator with custom values
helm install spark-operator spark-operator/spark-operator \
  -f 04-spark-operator-helm-values.yaml \
  -n spark-pipeline

# Verify operator is running
kubectl get pods -n spark-pipeline -l app.kubernetes.io/name=spark-operator
```

### Step 5: Deploy Networking & Security

```bash
kubectl apply -f 07-networking.yaml
kubectl apply -f 09-security.yaml
```

### Step 6: Deploy Monitoring

```bash
kubectl apply -f 08-monitoring.yaml

# Verify ServiceMonitors are created
kubectl get servicemonitor -n spark-pipeline
```

### Step 7: Deploy Auto-Scaling

```bash
kubectl apply -f 06-autoscaling.yaml

# Verify HPA is created
kubectl get hpa -n spark-pipeline
```

### Step 8: Deploy SparkApplication

```bash
# Update image reference and S3 paths in 05-spark-application.yaml
kubectl apply -f 05-spark-application.yaml

# Watch application status
kubectl get sparkapplication -n spark-pipeline -w
```

### Step 9: Deploy Disaster Recovery

```bash
kubectl apply -f 10-disaster-recovery.yaml

# Verify CronJobs are scheduled
kubectl get cronjobs -n spark-pipeline
```

## Verification

### Check Driver Pod

```bash
kubectl get pods -n spark-pipeline -l component=driver
kubectl logs -f <driver-pod-name> -n spark-pipeline
```

### Check Executor Pods

```bash
kubectl get pods -n spark-pipeline -l component=executor
kubectl top pods -n spark-pipeline  # Check resource usage
```

### Access Spark UI

```bash
# Port-forward to Spark UI service
kubectl port-forward svc/spark-ui 4040:4040 -n spark-pipeline

# Open browser: http://localhost:4040
```

### Check Metrics

```bash
# Query Prometheus for Spark metrics
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open browser: http://localhost:9090
# Query: spark_app_executor_activeCount
```

### Verify Auto-Scaling

```bash
# Generate load to trigger HPA
kubectl run -i --tty load-generator --rm --image=busybox -n spark-pipeline --restart=Never -- /bin/sh

# Watch HPA scale executors
kubectl get hpa spark-executor-hpa -n spark-pipeline -w
```

## Troubleshooting

### Driver Pod Crashes

```bash
# Check driver logs
kubectl logs <driver-pod> -n spark-pipeline --previous

# Check events
kubectl describe pod <driver-pod> -n spark-pipeline

# Check restart count
kubectl get pod <driver-pod> -n spark-pipeline -o jsonpath='{.status.containerStatuses[0].restartCount}'
```

### Checkpoint Recovery Failing

```bash
# Check PVC mount
kubectl describe pod <driver-pod> -n spark-pipeline | grep -A5 Mounts

# Verify checkpoint files exist
kubectl exec <driver-pod> -n spark-pipeline -- ls -lah /mnt/checkpoints

# Restore from backup
kubectl create job --from=cronjob/checkpoint-backup checkpoint-restore-manual -n spark-pipeline
```

### Executors Not Scaling

```bash
# Check HPA status
kubectl describe hpa spark-executor-hpa -n spark-pipeline

# Verify metrics are available
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/spark-pipeline/pods

# Check resource requests/limits
kubectl get pod <executor-pod> -n spark-pipeline -o yaml | grep -A4 resources
```

### Network Issues

```bash
# Test driver-executor connectivity
kubectl exec <executor-pod> -n spark-pipeline -- nc -zv <driver-pod-ip> 7078

# Check NetworkPolicy
kubectl describe networkpolicy -n spark-pipeline

# Verify DNS resolution
kubectl exec <driver-pod> -n spark-pipeline -- nslookup spark-driver-headless
```

## Performance Tuning

### Executor Memory Optimization

Adjust executor memory based on workload:

```yaml
executor:
  memory: "16g"  # Increase for data-intensive jobs
  memoryOverhead: "4g"  # 25% of executor memory recommended
```

### Checkpoint Interval

Balance recovery speed vs. overhead:

```yaml
sparkConf:
  "spark.streaming.checkpoint.interval": "30s"  # Longer interval = less overhead
```

### Storage Performance

Use high-performance storage class:

```yaml
storageClassName: spark-checkpoint-ssd
parameters:
  type: gp3
  iopsPerGB: "100"  # Increase IOPS for faster checkpointing
  throughput: "250"
```

## Cost Optimization

### Use Spot Instances for Executors

```yaml
executor:
  tolerations:
    - key: "workload-type"
      value: "spot"
      effect: "NoSchedule"
```

### Auto-Scaling Tuning

Reduce executor count during low traffic:

```yaml
spec:
  minReplicas: 1  # Lower minimum (default: 3)
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 600  # Longer delay before scaling down
```

### Event Log Cleanup

Archive old logs to cheaper storage:

```yaml
# Already configured in 10-disaster-recovery.yaml
# Archives logs > 7 days to S3 Glacier
```

## Security Best Practices

1. **Enable Pod Security Standards**: Use `restricted` profile
2. **Rotate Secrets**: Use External Secrets Operator with auto-rotation
3. **Network Segmentation**: Review NetworkPolicies for least privilege
4. **Audit Logging**: Enable Kubernetes audit logs for security events
5. **Image Scanning**: Use Trivy/Clair to scan Spark images for vulnerabilities
6. **TLS Everywhere**: Enable Spark SSL/TLS for all communication

## Monitoring Dashboards

Import Grafana dashboard:

```bash
# Dashboard JSON in 08-monitoring.yaml ConfigMap
kubectl get configmap spark-dashboard -n spark-pipeline -o jsonpath='{.data.spark-dashboard\.json}' > spark-dashboard.json

# Import to Grafana UI or via API
```

Key metrics to watch:
- Active executors
- Processing delay
- Task failure rate
- Memory utilization
- GC overhead
- Checkpoint success rate

## Disaster Recovery Testing

### Test Checkpoint Restore

```bash
# 1. Trigger manual backup
kubectl create job --from=cronjob/checkpoint-backup checkpoint-backup-test -n spark-pipeline

# 2. Delete Spark application
kubectl delete sparkapplication spark-streaming-pipeline -n spark-pipeline

# 3. Restore checkpoint
kubectl create job --from=job/checkpoint-restore checkpoint-restore-test -n spark-pipeline

# 4. Recreate application
kubectl apply -f 05-spark-application.yaml

# 5. Verify recovery
kubectl logs -f <new-driver-pod> -n spark-pipeline | grep "Recovered from checkpoint"
```

## License

This architecture is provided as-is for educational and production use. Adapt to your specific requirements.

## Contributing

Improvements welcome! Key areas:
- Multi-region failover automation
- Cost optimization patterns
- Advanced KEDA scaling triggers
- GPU support for ML workloads
