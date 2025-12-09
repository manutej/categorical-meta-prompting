# Self-Healing Features Quick Reference

This document provides a quick reference for all self-healing mechanisms implemented in the Spark pipeline architecture.

## Self-Healing Matrix

| Feature | Trigger | Response | Recovery Time | Configuration Location |
|---------|---------|----------|---------------|------------------------|
| **Pod Restart** | Exit code != 0 | Auto-restart up to 5 times | 30s + startup | `05-spark-application.yaml` |
| **Liveness Probe** | HTTP 4040 unresponsive | Kill and restart pod | 90s | `05-spark-application.yaml` |
| **Readiness Probe** | HTTP 4040 not ready | Remove from service | 30s | `05-spark-application.yaml` |
| **Checkpoint Recovery** | Driver restart | Restore from last checkpoint | <10s + startup | `03-storage.yaml`, `05-spark-application.yaml` |
| **Executor Scale-Up** | CPU > 70% or high lag | Add executors (50% increase) | 60s + pod startup | `06-autoscaling.yaml` |
| **Executor Scale-Down** | Low CPU for 5min | Remove executors (10% at a time) | 300s | `06-autoscaling.yaml` |
| **VPA Optimization** | Resource inefficiency | Adjust requests/limits | Next pod restart | `06-autoscaling.yaml` |
| **PDB Protection** | Node drain | Prevent disruption if < min | Immediate | `06-autoscaling.yaml` |
| **Alert: Driver Down** | Driver unresponsive > 2min | Notify ops team | Immediate | `08-monitoring.yaml` |
| **Alert: High Executor Failure** | Failure rate > 0.1/s | Notify ops team | Immediate | `08-monitoring.yaml` |
| **Alert: Streaming Delay** | Delay > 30s | Notify ops team | Immediate | `08-monitoring.yaml` |
| **Alert: Memory Pressure** | Memory > 90% | Notify ops team | Immediate | `08-monitoring.yaml` |
| **Alert: Checkpoint Failure** | Write failed | Critical alert | Immediate | `08-monitoring.yaml` |
| **Backup: Checkpoints** | Every 6 hours | S3 sync | 6h RPO | `10-disaster-recovery.yaml` |
| **Backup: Volume Snapshot** | Every 12 hours | CSI snapshot | 12h RPO | `10-disaster-recovery.yaml` |
| **Restore: Checkpoints** | Manual trigger | S3 restore | 15min RTO | `10-disaster-recovery.yaml` |
| **Network Retry** | Connection timeout | Retry with backoff | 300s timeout | `05-spark-application.yaml` |
| **Task Retry** | Task failure | Retry up to 4 times | Per task | `05-spark-application.yaml` |

## Self-Healing Decision Tree

```
Pod Failure
    │
    ├─→ Exit Code != 0
    │   └─→ restartPolicy: OnFailure
    │       └─→ Retry 5 times with 30s interval
    │           ├─→ Success: Continue
    │           └─→ Failure: Alert + Manual intervention
    │
    ├─→ Liveness Probe Failed (3x30s)
    │   └─→ Kill pod
    │       └─→ Kubelet restarts
    │           └─→ Checkpoint recovery
    │
    ├─→ OOM (Out of Memory)
    │   └─→ Pod killed
    │       ├─→ VPA adjusts memory requests
    │       └─→ Restart with higher memory
    │
    └─→ Node Failure
        └─→ Pod rescheduled to healthy node
            └─→ Checkpoint recovery from PVC

Performance Degradation
    │
    ├─→ CPU > 70%
    │   └─→ HPA: Scale up executors (+50%)
    │       └─→ Distribute load
    │
    ├─→ Memory > 90%
    │   ├─→ Alert ops team
    │   └─→ VPA recommendation (apply on restart)
    │
    ├─→ Processing Delay > 30s
    │   ├─→ Alert ops team
    │   └─→ HPA: Scale up if within limits
    │
    └─→ High Task Failure Rate
        ├─→ Alert ops team (investigate data quality)
        └─→ Task retry (up to 4 times)

Data Loss Prevention
    │
    ├─→ Checkpoint Write Failure
    │   ├─→ Critical alert
    │   └─→ Manual intervention required
    │
    ├─→ Driver Crash Before Checkpoint
    │   └─→ Restart from last successful checkpoint
    │       └─→ RPO = checkpoint interval (10s)
    │
    └─→ PVC Corruption
        └─→ Restore from S3 backup
            ├─→ RPO = 6 hours (backup frequency)
            └─→ RTO = 15 minutes

Disaster Scenarios
    │
    ├─→ Cluster Failure
    │   └─→ Restore in new cluster
    │       ├─→ Deploy manifests
    │       ├─→ Restore checkpoints from S3
    │       └─→ Start SparkApplication
    │
    ├─→ Region Failure
    │   └─→ Failover to secondary region
    │       ├─→ S3 cross-region replication
    │       ├─→ DNS/Ingress update
    │       └─→ Start in secondary cluster
    │
    └─→ Data Corruption
        └─→ Restore from volume snapshot
            ├─→ List snapshots
            ├─→ Create PVC from snapshot
            └─→ Update SparkApplication
```

## Configuration Snippets

### 1. Restart Policy (OnFailure)

```yaml
# 05-spark-application.yaml
restartPolicy:
  type: OnFailure
  onFailureRetries: 5
  onFailureRetryInterval: 30
  onSubmissionFailureRetries: 3
  onSubmissionFailureRetryInterval: 60
```

**How it works**:
- Driver pod exits with non-zero code → Operator waits 30s → Restarts
- Repeats up to 5 times
- After 5 failures → SparkApplication marked as Failed

### 2. Health Probes

```yaml
# 05-spark-application.yaml
driver:
  livenessProbe:
    httpGet:
      path: /
      port: 4040
    initialDelaySeconds: 60
    periodSeconds: 30
    timeoutSeconds: 10
    failureThreshold: 3
  readinessProbe:
    httpGet:
      path: /
      port: 4040
    initialDelaySeconds: 30
    periodSeconds: 10
    failureThreshold: 3
```

**How it works**:
- **Liveness**: Kubelet checks every 30s. If 3 consecutive failures → Kill pod → Restart
- **Readiness**: Kubelet checks every 10s. If failed → Remove from service endpoints

### 3. Checkpoint Recovery

```yaml
# 05-spark-application.yaml
sparkConf:
  "spark.streaming.receiver.writeAheadLog.enable": "true"

volumes:
  - name: checkpoint-storage
    persistentVolumeClaim:
      claimName: spark-checkpoint-pvc

arguments:
  - "--checkpoint-path=/mnt/checkpoints/streaming-app"
```

**How it works**:
- Spark writes state to `/mnt/checkpoints` every 10s
- On driver restart → Reads from checkpoint → Continues from last state
- WAL ensures no data loss during checkpoint interval

### 4. HPA Auto-Scaling

```yaml
# 06-autoscaling.yaml
spec:
  minReplicas: 3
  maxReplicas: 20
  behavior:
    scaleUp:
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70
```

**How it works**:
- CPU > 70% → Add 50% more executors (max 20)
- CPU < 70% for 5min → Remove 10% of executors (min 3)
- Prevents thrashing with stabilization windows

### 5. PodDisruptionBudget

```yaml
# 06-autoscaling.yaml
spec:
  minAvailable: 2  # For executors
  selector:
    matchLabels:
      component: executor
```

**How it works**:
- During node drain → Kubernetes ensures at least 2 executors remain running
- Blocks eviction if < minAvailable
- Applies to voluntary disruptions only (not pod crashes)

### 6. Alerting Rules

```yaml
# 08-monitoring.yaml
- alert: SparkDriverDown
  expr: up{job="spark-driver-metrics"} == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Spark driver pod is down"
```

**How it works**:
- Prometheus scrapes metrics every 30s
- If driver metric missing for 2min → Fire alert
- AlertManager routes to Slack/PagerDuty

### 7. Checkpoint Backup

```yaml
# 10-disaster-recovery.yaml
schedule: "0 */6 * * *"  # Every 6 hours
command:
  - aws s3 sync /mnt/checkpoints s3://backups/checkpoints/${TIMESTAMP}/
```

**How it works**:
- CronJob runs every 6 hours
- Syncs checkpoint directory to S3
- Deletes backups older than 7 days
- RPO = 6 hours (worst case)

### 8. Volume Snapshots

```yaml
# 10-disaster-recovery.yaml
schedule: "0 */12 * * *"  # Every 12 hours
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: spark-checkpoint-pvc
```

**How it works**:
- CronJob creates VolumeSnapshot via CSI driver
- Snapshot stored in cloud provider's snapshot service
- Deletes snapshots older than 7 days
- RPO = 12 hours

## Self-Healing Metrics

### Key Performance Indicators

| Metric | Target | Alert Threshold | Self-Healing Action |
|--------|--------|-----------------|---------------------|
| **Uptime** | 99.9% | < 99% | Investigate restart frequency |
| **Recovery Time** | < 2min | > 5min | Optimize checkpoint interval |
| **Checkpoint Success Rate** | 100% | < 99% | Critical alert |
| **Executor Availability** | > 80% | < 60% | Scale up, investigate failures |
| **Processing Delay** | < 10s | > 30s | Scale up, optimize code |
| **Task Failure Rate** | < 0.1% | > 1% | Investigate data quality |
| **Restart Count** | 0/day | > 5/day | Investigate root cause |

### Prometheus Queries

```promql
# Average recovery time (checkpoint to running)
histogram_quantile(0.95,
  rate(spark_streaming_checkpoint_lastCheckpointDuration[5m])
)

# Executor failure rate
rate(spark_app_executor_failureCount[5m])

# Processing delay
spark_streaming_lastReceivedBatch_processingDelay

# HPA scaling events
rate(kube_horizontalpodautoscaler_status_current_replicas[5m])

# Restart count over 24h
increase(kube_pod_container_status_restarts_total{namespace="spark-pipeline"}[24h])
```

## Testing Self-Healing

### Test 1: Driver Pod Failure

```bash
# Kill driver pod
kubectl delete pod -n spark-pipeline -l component=driver

# Expected behavior:
# - Pod is recreated within 30s
# - Checkpoint recovery starts
# - Application continues from last state
# - Alert fires if down > 2min

# Verify
kubectl get pods -n spark-pipeline -l component=driver -w
kubectl logs -f <new-driver-pod> -n spark-pipeline | grep "Recovered"
```

### Test 2: Executor Failure

```bash
# Kill executor pod
kubectl delete pod -n spark-pipeline -l component=executor | head -1

# Expected behavior:
# - Spark driver detects missing executor
# - Driver requests new executor
# - Operator creates replacement pod
# - Tasks redistributed

# Verify
kubectl get pods -n spark-pipeline -l component=executor -w
```

### Test 3: CPU Pressure (HPA)

```bash
# Generate high CPU load
# Option 1: Increase input data rate
# Option 2: Reduce executor count temporarily

# Expected behavior:
# - CPU > 70% detected by HPA
# - HPA scales up executors (+50%)
# - Load distributes across new executors
# - CPU returns to < 70%

# Verify
kubectl get hpa spark-executor-hpa -n spark-pipeline -w
kubectl top pods -n spark-pipeline
```

### Test 4: Node Failure

```bash
# Simulate node failure
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# Expected behavior:
# - Pods on node are evicted
# - PDB ensures minimum executors remain
# - Pods rescheduled to other nodes
# - Driver recovers from checkpoint if evicted

# Verify
kubectl get pods -n spark-pipeline -o wide -w
```

### Test 5: Checkpoint Recovery

```bash
# Manually trigger checkpoint, then restart
kubectl exec -n spark-pipeline <driver-pod> -- touch /tmp/trigger-checkpoint
sleep 30
kubectl delete pod -n spark-pipeline -l component=driver

# Expected behavior:
# - New driver starts
# - Reads checkpoint from PVC
# - Continues from last committed offset
# - No data loss

# Verify
kubectl logs -f <new-driver-pod> -n spark-pipeline | grep -i checkpoint
```

### Test 6: Disaster Recovery

```bash
# Simulate data center failure
# 1. Create backup
kubectl create job --from=cronjob/checkpoint-backup checkpoint-backup-test -n spark-pipeline
kubectl wait --for=condition=complete job/checkpoint-backup-test -n spark-pipeline

# 2. Delete everything
kubectl delete namespace spark-pipeline

# 3. Restore
kubectl create namespace spark-pipeline
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-rbac.yaml
kubectl apply -f 03-storage.yaml

# 4. Restore checkpoint
kubectl create job --from=job/checkpoint-restore checkpoint-restore-test -n spark-pipeline
kubectl wait --for=condition=complete job/checkpoint-restore-test -n spark-pipeline

# 5. Deploy SparkApplication
kubectl apply -f 05-spark-application.yaml

# Expected behavior:
# - All resources recreated
# - Checkpoint restored from S3
# - Application starts from last backup
# - RPO = 6 hours (backup frequency)

# Verify
kubectl get all -n spark-pipeline
kubectl logs -f <driver-pod> -n spark-pipeline | grep "Recovered"
```

## Failure Scenarios & Responses

| Scenario | Probability | Impact | Self-Healing | Manual Action Needed |
|----------|-------------|--------|--------------|----------------------|
| **Driver pod crash** | High | High | Auto-restart + checkpoint recovery | None (if < 5 retries) |
| **Executor pod crash** | Medium | Low | Driver creates replacement | None |
| **Node failure** | Medium | Medium | Pods rescheduled + recovery | None |
| **Cluster failure** | Low | High | Manual restore from S3 | Yes (deploy + restore) |
| **PVC corruption** | Low | High | Restore from snapshot | Yes (create PVC from snapshot) |
| **S3 outage** | Low | High | Retry + local buffer | Monitor, may need fallback |
| **Checkpoint write failure** | Low | Critical | Alert only | Investigate storage issue |
| **OOM (driver)** | Medium | High | Restart + VPA adjustment | Review memory config |
| **OOM (executor)** | Medium | Low | Executor recreated | Review executor memory |
| **High processing delay** | Medium | Medium | HPA scale-up | Review code efficiency |
| **Kafka lag** | Medium | Medium | HPA scale-up | Review consumer config |
| **Network partition** | Low | High | Retry with backoff | Check network policies |

## Best Practices

1. **Set appropriate checkpoint interval**: Balance recovery speed vs. overhead (10-60s)
2. **Monitor restart count**: > 5/day indicates underlying issue
3. **Test recovery regularly**: Monthly DR drills
4. **Tune HPA thresholds**: Based on actual workload patterns
5. **Use PDBs conservatively**: Don't set too high, blocks cluster upgrades
6. **Alert fatigue prevention**: Set appropriate thresholds and windows
7. **Document runbooks**: For scenarios requiring manual intervention
8. **Capacity planning**: Ensure cluster can handle max replicas
9. **Cost optimization**: Use spot instances for executors (tolerant to failures)
10. **Observability**: Comprehensive logging and metrics for debugging

## Further Reading

- [Spark Streaming Guide](https://spark.apache.org/docs/latest/streaming-programming-guide.html)
- [Kubernetes Self-Healing](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Disaster Recovery Best Practices](https://velero.io/docs/main/disaster-case/)
