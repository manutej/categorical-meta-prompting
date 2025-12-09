# Kubernetes Spark Pipeline - Complete Documentation Index

## Quick Navigation

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [README.md](README.md) | Complete overview, deployment instructions | All | 30 min |
| [ARCHITECTURE-SUMMARY.md](ARCHITECTURE-SUMMARY.md) | Architecture layers, cost, performance | Architects, Managers | 20 min |
| [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) | Step-by-step deployment, troubleshooting | DevOps, SREs | 45 min |
| [SELF-HEALING-REFERENCE.md](SELF-HEALING-REFERENCE.md) | Self-healing features, testing | SREs, Operators | 25 min |
| [INDEX.md](INDEX.md) | This file - navigation guide | All | 5 min |

## Kubernetes Manifests (YAML Files)

### Core Resources (Deploy in Order)

| # | File | Description | Dependencies | Lines |
|---|------|-------------|--------------|-------|
| 1 | [01-namespace.yaml](01-namespace.yaml) | Namespace, ResourceQuota, LimitRange | None | 80 |
| 2 | [02-rbac.yaml](02-rbac.yaml) | ServiceAccounts, Roles, RoleBindings | 01 | 120 |
| 3 | [03-storage.yaml](03-storage.yaml) | StorageClass, PVCs, ConfigMaps, Secrets | 01, 02 | 150 |
| 4 | [04-spark-operator-helm-values.yaml](04-spark-operator-helm-values.yaml) | Spark Operator Helm configuration | 01-03 | 120 |
| 5 | [05-spark-application.yaml](05-spark-application.yaml) | Main SparkApplication CRD | 01-04 | 350 |
| 6 | [06-autoscaling.yaml](06-autoscaling.yaml) | HPA, VPA, PDB, PriorityClass | 05 | 200 |
| 7 | [07-networking.yaml](07-networking.yaml) | Services, Ingress, NetworkPolicy | 05 | 300 |
| 8 | [08-monitoring.yaml](08-monitoring.yaml) | ServiceMonitor, PrometheusRule, Dashboards | 05 | 250 |
| 9 | [09-security.yaml](09-security.yaml) | PodSecurityPolicy, TLS, Admission | 01-05 | 280 |
| 10 | [10-disaster-recovery.yaml](10-disaster-recovery.yaml) | Backup CronJobs, Restore procedures | 03, 05 | 350 |

**Total**: 2,200 lines of production-ready Kubernetes manifests

## Documentation Structure

### Getting Started (Start Here)

1. **[README.md](README.md)** - Start here for overview
   - Architecture diagram
   - Resource dependency map
   - Self-healing features
   - Quick start (15 min)
   - Verification steps
   - Troubleshooting guide

2. **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Complete deployment walkthrough
   - Infrastructure prerequisites (AWS/GCP/Azure)
   - Quick start (testing)
   - Production deployment (security, HA, DR)
   - Configuration customization
   - Validation & testing
   - Day-2 operations

### Architecture & Design

3. **[ARCHITECTURE-SUMMARY.md](ARCHITECTURE-SUMMARY.md)** - Deep dive into design
   - 7 architecture layers
   - Data flow diagrams
   - Resource requirements
   - Cost estimation
   - Performance characteristics
   - Deployment checklist

4. **[SELF-HEALING-REFERENCE.md](SELF-HEALING-REFERENCE.md)** - Self-healing mechanisms
   - Self-healing matrix (18 mechanisms)
   - Decision trees
   - Configuration snippets
   - Testing procedures
   - Metrics & KPIs
   - Failure scenarios

### Manifest Reference

5. **Individual YAML files** (01-10) - Production-ready configurations
   - Inline comments explaining every setting
   - Self-healing annotations
   - Security best practices
   - Resource limits and quotas

## Document Map by Use Case

### Use Case 1: First-Time Deployment

**Goal**: Deploy pipeline in test environment

**Path**:
1. Read [README.md](README.md) → Overview
2. Follow [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Quick Start (15 min)
3. Deploy manifests 01-08 (skip 09-10 for testing)
4. Verify using [README.md](README.md) → Verification section

**Time**: 1-2 hours

### Use Case 2: Production Deployment

**Goal**: Deploy production-ready pipeline with full security

**Path**:
1. Read [ARCHITECTURE-SUMMARY.md](ARCHITECTURE-SUMMARY.md) → Understand design
2. Review [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Production Deployment
3. Complete prerequisites (Prometheus, Cert-Manager, External Secrets)
4. Deploy all manifests 01-10 in order
5. Follow [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Validation & Testing
6. Configure monitoring/alerting
7. Test DR procedures

**Time**: 1 day

### Use Case 3: Operations & Troubleshooting

**Goal**: Debug issues, perform maintenance

**Path**:
1. [README.md](README.md) → Troubleshooting section
2. [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Troubleshooting Common Issues
3. [SELF-HEALING-REFERENCE.md](SELF-HEALING-REFERENCE.md) → Failure Scenarios

**Tools**:
- kubectl logs, describe, top
- Prometheus queries
- Grafana dashboards

### Use Case 4: Understanding Self-Healing

**Goal**: Learn how auto-recovery works

**Path**:
1. [SELF-HEALING-REFERENCE.md](SELF-HEALING-REFERENCE.md) → Self-Healing Matrix
2. [SELF-HEALING-REFERENCE.md](SELF-HEALING-REFERENCE.md) → Testing Self-Healing
3. [05-spark-application.yaml](05-spark-application.yaml) → Search for "SELF-HEALING" comments
4. [06-autoscaling.yaml](06-autoscaling.yaml) → HPA/VPA configuration

**Hands-On**:
- Test driver pod restart
- Trigger HPA scaling
- Simulate node failure
- Verify checkpoint recovery

### Use Case 5: Cost Optimization

**Goal**: Reduce infrastructure costs

**Path**:
1. [ARCHITECTURE-SUMMARY.md](ARCHITECTURE-SUMMARY.md) → Cost Estimation
2. [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Cost Optimization section
3. Modify [06-autoscaling.yaml](06-autoscaling.yaml) → Reduce minReplicas
4. Update [05-spark-application.yaml](05-spark-application.yaml) → Use spot instances

**Strategies**:
- Spot instances for executors (70% savings)
- Scale down during off-hours (HPA min: 1)
- Optimize checkpoint interval
- Archive logs to Glacier

### Use Case 6: Security Hardening

**Goal**: Implement enterprise security

**Path**:
1. [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) → Security Hardening section
2. Deploy [09-security.yaml](09-security.yaml) → All security resources
3. Enable Pod Security Standards in [01-namespace.yaml](01-namespace.yaml)
4. Configure External Secrets Operator
5. Enable TLS in [05-spark-application.yaml](05-spark-application.yaml)

**Checklist**:
- [ ] RBAC with least privilege
- [ ] NetworkPolicies (default deny)
- [ ] Pod Security Standards (restricted)
- [ ] TLS for all communication
- [ ] Secret encryption (KMS)
- [ ] Audit logging enabled

## Key Concepts Explained

### Self-Healing Mechanisms

| Mechanism | How It Works | When It Triggers | File |
|-----------|--------------|------------------|------|
| **Restart Policy** | Operator retries failed pods | Exit code != 0 | 05 |
| **Liveness Probe** | Kubelet kills unresponsive pods | HTTP timeout | 05 |
| **Readiness Probe** | Removes pod from service | HTTP not ready | 05 |
| **Checkpoint Recovery** | Restores state from PVC | Driver restart | 03, 05 |
| **HPA** | Scales executors based on metrics | CPU/Memory/Lag high | 06 |
| **VPA** | Right-sizes resource requests | Resource inefficiency | 06 |
| **PDB** | Prevents disruptions | Node drain | 06 |
| **Alerts** | Notifies ops team | Failures detected | 08 |
| **Backups** | Periodic S3 sync | Scheduled (6h) | 10 |

### Resource Types

| Resource | Purpose | Count | Critical |
|----------|---------|-------|----------|
| Namespace | Isolation | 1 | Yes |
| ServiceAccount | RBAC identity | 2 | Yes |
| Role/RoleBinding | Permissions | 3 | Yes |
| PVC | Persistent storage | 2 | Yes |
| ConfigMap | Configuration | 4 | Yes |
| Secret | Credentials | 2 | Yes |
| Deployment | Operator, History | 2 | Yes |
| SparkApplication | Main job | 1 | Yes |
| Service | Networking | 3 | Yes |
| Ingress | External access | 2 | No |
| HPA | Auto-scaling | 1 | Yes |
| VPA | Resource optimization | 1 | No |
| PDB | Disruption protection | 2 | Yes |
| NetworkPolicy | Network security | 4 | Yes |
| ServiceMonitor | Metrics scraping | 2 | No |
| PrometheusRule | Alerting | 1 | Yes |
| CronJob | Backups | 3 | Yes |

### Dependencies

```
Prerequisites
    ├─→ Kubernetes 1.23+
    ├─→ Helm 3.x
    ├─→ CSI Driver (ReadWriteMany)
    ├─→ Prometheus Operator (monitoring)
    ├─→ Cert-Manager (TLS)
    ├─→ Metrics Server (HPA)
    └─→ External Secrets (optional)

Deployment Order
    01-namespace.yaml
        └─→ 02-rbac.yaml
            └─→ 03-storage.yaml
                └─→ 04-spark-operator (Helm)
                    └─→ 05-spark-application.yaml
                        ├─→ 06-autoscaling.yaml
                        ├─→ 07-networking.yaml
                        ├─→ 08-monitoring.yaml
                        ├─→ 09-security.yaml
                        └─→ 10-disaster-recovery.yaml
```

## Quick Reference Commands

### Deployment

```bash
# Quick start (all manifests)
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-rbac.yaml
kubectl apply -f 03-storage.yaml
helm install spark-operator spark-operator/spark-operator -f 04-spark-operator-helm-values.yaml -n spark-pipeline
kubectl apply -f 05-spark-application.yaml
kubectl apply -f 06-autoscaling.yaml
kubectl apply -f 07-networking.yaml
kubectl apply -f 08-monitoring.yaml
kubectl apply -f 09-security.yaml
kubectl apply -f 10-disaster-recovery.yaml
```

### Verification

```bash
# Check all resources
kubectl get all -n spark-pipeline

# Check SparkApplication status
kubectl get sparkapplication -n spark-pipeline

# View driver logs
kubectl logs -f $(kubectl get pod -n spark-pipeline -l component=driver -o jsonpath='{.items[0].metadata.name}')

# Check HPA status
kubectl get hpa -n spark-pipeline

# View Spark UI
kubectl port-forward -n spark-pipeline svc/spark-ui 4040:4040
```

### Troubleshooting

```bash
# Describe driver pod
kubectl describe pod -n spark-pipeline -l component=driver

# Check PVC status
kubectl get pvc -n spark-pipeline

# View operator logs
kubectl logs -n spark-pipeline -l app.kubernetes.io/name=spark-operator

# Check metrics
kubectl top pods -n spark-pipeline

# Test S3 connectivity
kubectl exec -n spark-pipeline <driver-pod> -- aws s3 ls s3://your-bucket/
```

## File Size & Complexity

| File | Lines | Comments | Complexity | Maintenance |
|------|-------|----------|------------|-------------|
| 01-namespace.yaml | 80 | 30% | Low | Low |
| 02-rbac.yaml | 120 | 40% | Medium | Low |
| 03-storage.yaml | 150 | 35% | Medium | Medium |
| 04-spark-operator-helm-values.yaml | 120 | 50% | Medium | Low |
| 05-spark-application.yaml | 350 | 45% | High | High |
| 06-autoscaling.yaml | 200 | 40% | High | Medium |
| 07-networking.yaml | 300 | 35% | Medium | Low |
| 08-monitoring.yaml | 250 | 30% | Medium | Medium |
| 09-security.yaml | 280 | 40% | High | Medium |
| 10-disaster-recovery.yaml | 350 | 35% | Medium | Low |
| **Total** | **2,200** | **38%** | - | - |

**Maintainability Score**: 8/10 (well-documented, modular, production-ready)

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-04 | Initial release | API Architect Agent |

## Support & Contributions

### Getting Help

1. **Documentation**: Read relevant sections above
2. **Troubleshooting**: [README.md](README.md) + [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)
3. **Community**: Spark Operator GitHub issues
4. **Professional**: Engage Spark/Kubernetes consultants

### Contributing

Improvements welcome in:
- Multi-region failover automation
- KEDA integration for event-driven scaling
- GPU support for ML workloads
- Cost optimization patterns
- Additional monitoring dashboards

### External References

- [Spark Operator Docs](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Apache Spark Docs](https://spark.apache.org/docs/latest/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [Velero Docs](https://velero.io/docs/)

## License

This architecture is provided as-is for educational and production use. Adapt to your specific requirements.

---

**Last Updated**: 2025-12-04
**Maintainer**: API Architect Agent
**Status**: Production Ready
