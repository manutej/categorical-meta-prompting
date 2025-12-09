# Spark Pipeline Deployment Guide

Complete step-by-step guide for deploying the self-healing Spark data pipeline on Kubernetes.

## Table of Contents

1. [Infrastructure Prerequisites](#infrastructure-prerequisites)
2. [Quick Start (15 minutes)](#quick-start-15-minutes)
3. [Production Deployment](#production-deployment)
4. [Configuration Customization](#configuration-customization)
5. [Validation & Testing](#validation--testing)
6. [Day-2 Operations](#day-2-operations)

---

## Infrastructure Prerequisites

### Required Components

| Component | Version | Purpose | Installation |
|-----------|---------|---------|--------------|
| Kubernetes | 1.23+ | Container orchestration | Cloud provider or kubeadm |
| Helm | 3.x | Package manager | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |
| kubectl | 1.23+ | CLI tool | Cloud provider CLI |
| CSI Driver | Latest | Persistent storage | Cloud provider specific |

### Optional but Recommended

| Component | Purpose | Priority |
|-----------|---------|----------|
| Prometheus Operator | Metrics & alerting | High |
| Cert-Manager | TLS certificate automation | High |
| Metrics Server | HPA metrics | High |
| External Secrets Operator | Secret management | Medium |
| Velero | Cluster backups | Medium |
| KEDA | Event-driven autoscaling | Low |
| OPA Gatekeeper | Policy enforcement | Low |

### Cloud Provider Setup

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name spark-pipeline \
  --version 1.28 \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 3 \
  --nodes-max 10 \
  --managed

# Install EBS CSI driver
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.25"

# Install EFS CSI driver (for ReadWriteMany)
kubectl apply -k "github.com/kubernetes-sigs/aws-efs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.7"

# Create EFS filesystem
aws efs create-file-system \
  --region us-west-2 \
  --performance-mode generalPurpose \
  --throughput-mode bursting \
  --tags Key=Name,Value=spark-checkpoint-efs
```

#### GCP GKE

```bash
# Create GKE cluster
gcloud container clusters create spark-pipeline \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-4 \
  --enable-autoscaling \
  --min-nodes 3 \
  --max-nodes 10 \
  --enable-stackdriver-kubernetes

# GKE comes with GCE Persistent Disk CSI driver pre-installed
# For ReadWriteMany, use Filestore CSI driver
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/gcp-filestore-csi-driver/master/deploy/kubernetes/overlays/stable/deploy-driver.yaml
```

#### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group spark-pipeline-rg \
  --name spark-pipeline \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group spark-pipeline-rg --name spark-pipeline

# AKS comes with Azure Disk CSI driver pre-installed
# For ReadWriteMany, use Azure Files CSI driver (pre-installed)
```

---

## Quick Start (15 minutes)

For testing purposes, deploy with minimal configuration.

### Step 1: Clone Configuration

```bash
# Navigate to k8s-spark-pipeline directory
cd k8s-spark-pipeline
```

### Step 2: Install Core Operators

```bash
# Install Prometheus Operator (for monitoring)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Install Metrics Server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Step 3: Update Configuration

```bash
# Edit S3 credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Create secret imperatively (quick start only)
kubectl create namespace spark-pipeline
kubectl create secret generic spark-s3-credentials \
  -n spark-pipeline \
  --from-literal=AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  --from-literal=AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"

# Update S3 bucket names in 03-storage.yaml
sed -i '' 's/spark-pipeline-input/your-input-bucket/g' 03-storage.yaml
sed -i '' 's/spark-pipeline-output/your-output-bucket/g' 03-storage.yaml
sed -i '' 's/spark-pipeline-checkpoints/your-checkpoint-bucket/g' 03-storage.yaml

# Update Spark application image in 05-spark-application.yaml
sed -i '' 's|your-registry/spark-pipeline:3.5.0-v1.0.0|your-actual-image|g' 05-spark-application.yaml
```

### Step 4: Deploy Resources

```bash
# Deploy namespace and RBAC
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-rbac.yaml

# Deploy storage (skip secret creation, already done)
kubectl apply -f 03-storage.yaml

# Install Spark Operator
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update
helm install spark-operator spark-operator/spark-operator \
  -f 04-spark-operator-helm-values.yaml \
  -n spark-pipeline

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=spark-operator -n spark-pipeline --timeout=300s

# Deploy networking
kubectl apply -f 07-networking.yaml

# Deploy monitoring
kubectl apply -f 08-monitoring.yaml

# Deploy autoscaling
kubectl apply -f 06-autoscaling.yaml

# Deploy SparkApplication
kubectl apply -f 05-spark-application.yaml
```

### Step 5: Verify Deployment

```bash
# Check operator
kubectl get pods -n spark-pipeline -l app.kubernetes.io/name=spark-operator

# Check SparkApplication
kubectl get sparkapplication -n spark-pipeline

# Check driver pod
kubectl get pods -n spark-pipeline -l component=driver

# Check executor pods
kubectl get pods -n spark-pipeline -l component=executor

# View driver logs
kubectl logs -f $(kubectl get pod -n spark-pipeline -l component=driver -o jsonpath='{.items[0].metadata.name}')
```

---

## Production Deployment

For production environments with full security and reliability features.

### Step 1: Security Hardening

#### 1.1 Use External Secrets Operator

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system --create-namespace

# Configure AWS Secrets Manager backend
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: spark-pipeline
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        jwt:
          serviceAccountRef:
            name: spark
EOF

# Create external secret
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: spark-s3-credentials
  namespace: spark-pipeline
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: spark-s3-credentials
  data:
    - secretKey: AWS_ACCESS_KEY_ID
      remoteRef:
        key: spark/s3-credentials
        property: access_key_id
    - secretKey: AWS_SECRET_ACCESS_KEY
      remoteRef:
        key: spark/s3-credentials
        property: secret_access_key
EOF

# Comment out static secret in 03-storage.yaml
```

#### 1.2 Install Cert-Manager for TLS

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace --set installCRDs=true

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Update ingress annotations in 07-networking.yaml to use cert-manager
```

#### 1.3 Enable Pod Security Standards

```bash
# Label namespace with Pod Security Standards
kubectl label namespace spark-pipeline \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

### Step 2: High Availability Configuration

#### 2.1 Multi-AZ Node Placement

```bash
# Ensure nodes are spread across availability zones
# AWS example:
eksctl create nodegroup \
  --cluster spark-pipeline \
  --name spark-compute-az1 \
  --node-zones us-west-2a \
  --node-type m5.2xlarge \
  --nodes 2

eksctl create nodegroup \
  --cluster spark-pipeline \
  --name spark-compute-az2 \
  --node-zones us-west-2b \
  --node-type m5.2xlarge \
  --nodes 2

eksctl create nodegroup \
  --cluster spark-pipeline \
  --name spark-compute-az3 \
  --node-zones us-west-2c \
  --node-type m5.2xlarge \
  --nodes 2
```

#### 2.2 Configure Topology Spread

Add to SparkApplication in `05-spark-application.yaml`:

```yaml
executor:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: spark-pipeline
          component: executor
```

### Step 3: Disaster Recovery Setup

#### 3.1 Install Velero

```bash
# Install Velero CLI
brew install velero  # macOS
# Or download from https://velero.io/docs/main/basic-install/

# Install Velero in cluster (AWS example)
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.8.0 \
  --bucket spark-pipeline-velero \
  --backup-location-config region=us-west-2 \
  --snapshot-location-config region=us-west-2 \
  --secret-file ./credentials-velero

# Enable volume snapshots
kubectl patch volumesnapshotclass csi-snapclass \
  -p '{"deletionPolicy":"Retain"}'
```

#### 3.2 Deploy DR Resources

```bash
kubectl apply -f 10-disaster-recovery.yaml

# Verify CronJobs are scheduled
kubectl get cronjobs -n spark-pipeline
```

### Step 4: Monitoring & Alerting

#### 4.1 Configure AlertManager

```bash
# Create AlertManager configuration
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-config
  namespace: monitoring
stringData:
  alertmanager.yaml: |
    global:
      resolve_timeout: 5m
      slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'spark-pipeline-team'
      routes:
      - match:
          severity: critical
        receiver: 'spark-pipeline-oncall'
    receivers:
    - name: 'spark-pipeline-team'
      slack_configs:
      - channel: '#spark-pipeline-alerts'
        title: 'Spark Pipeline Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    - name: 'spark-pipeline-oncall'
      slack_configs:
      - channel: '#spark-pipeline-critical'
        title: 'CRITICAL: Spark Pipeline'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
      pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
EOF
```

#### 4.2 Import Grafana Dashboards

```bash
# Get Grafana admin password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port-forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Import dashboard JSON from 08-monitoring.yaml ConfigMap
# Access Grafana at http://localhost:3000
# Login with admin/<password-from-above>
# Import dashboard from ConfigMap
```

### Step 5: Performance Tuning

#### 5.1 Resource Right-Sizing

```bash
# Install VPA (if not already installed)
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh

# Deploy VPA configuration
kubectl apply -f 06-autoscaling.yaml

# Monitor VPA recommendations
kubectl describe vpa spark-executor-vpa -n spark-pipeline
```

#### 5.2 Storage Optimization

```bash
# Update StorageClass for higher IOPS (AWS example)
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: spark-checkpoint-ssd-high-iops
provisioner: ebs.csi.aws.com
parameters:
  type: io2
  iopsPerGB: "100"
  throughput: "500"
  encrypted: "true"
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
EOF

# Update PVC to use new StorageClass
kubectl patch pvc spark-checkpoint-pvc -n spark-pipeline \
  -p '{"spec":{"storageClassName":"spark-checkpoint-ssd-high-iops"}}'
```

---

## Configuration Customization

### Spark Application Parameters

Edit `05-spark-application.yaml`:

```yaml
# Adjust executor count based on workload
executor:
  instances: 10  # Scale up for higher throughput

# Increase memory for data-intensive jobs
executor:
  memory: "16g"
  memoryOverhead: "4g"

# Tune checkpoint interval
sparkConf:
  "spark.streaming.checkpoint.interval": "60s"  # Longer = less overhead
```

### Auto-Scaling Thresholds

Edit `06-autoscaling.yaml`:

```yaml
# HPA: Adjust CPU target
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 60  # Lower = more aggressive scaling

# Adjust scaling behavior
behavior:
  scaleUp:
    policies:
      - type: Percent
        value: 100  # Double executors on scale-up
        periodSeconds: 60
```

### Storage Sizing

Edit `03-storage.yaml`:

```yaml
# Increase checkpoint storage
resources:
  requests:
    storage: 500Gi  # Increase for larger state

# Enable storage auto-expansion
allowVolumeExpansion: true
```

### Network Policies

Edit `07-networking.yaml` to restrict egress:

```yaml
# Restrict S3 access to specific IP ranges
egress:
  - to:
      - ipBlock:
          cidr: 52.92.0.0/16  # Your S3 endpoint range
    ports:
      - protocol: TCP
        port: 443
```

---

## Validation & Testing

### Functional Testing

```bash
# 1. Verify driver is running
kubectl wait --for=condition=ready pod -l component=driver -n spark-pipeline --timeout=300s

# 2. Check Spark UI
kubectl port-forward -n spark-pipeline svc/spark-ui 4040:4040
# Open http://localhost:4040

# 3. Verify checkpointing
DRIVER_POD=$(kubectl get pod -n spark-pipeline -l component=driver -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n spark-pipeline $DRIVER_POD -- ls -lah /mnt/checkpoints

# 4. Test data processing
kubectl logs -f $DRIVER_POD -n spark-pipeline | grep "Processed"
```

### Self-Healing Testing

```bash
# 1. Kill driver pod (should auto-restart)
kubectl delete pod -n spark-pipeline -l component=driver
kubectl wait --for=condition=ready pod -l component=driver -n spark-pipeline --timeout=300s

# 2. Kill executor pod (should be recreated)
kubectl delete pod -n spark-pipeline -l component=executor --field-selector=status.phase=Running | head -1
kubectl get pods -n spark-pipeline -l component=executor -w

# 3. Test checkpoint recovery
# Delete driver, wait for restart, check if state is recovered
kubectl delete pod -n spark-pipeline -l component=driver
sleep 60
kubectl logs -f $DRIVER_POD -n spark-pipeline | grep "Recovered from checkpoint"
```

### Auto-Scaling Testing

```bash
# Generate load to trigger HPA
# Option 1: Increase input data rate
# Option 2: Manually set high CPU usage

# Watch HPA scale executors
kubectl get hpa spark-executor-hpa -n spark-pipeline -w

# Verify executors are added
kubectl get pods -n spark-pipeline -l component=executor -w
```

### Monitoring Testing

```bash
# Verify metrics are being scraped
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Query Spark metrics in Prometheus
# Open http://localhost:9090
# Query: spark_app_executor_activeCount

# Verify alerts are configured
# Open http://localhost:9090/alerts
# Look for "SparkDriverDown", "HighExecutorFailureRate", etc.
```

---

## Day-2 Operations

### Upgrading Spark Version

```bash
# 1. Build new Spark image
docker build -t your-registry/spark-pipeline:3.5.1-v1.1.0 .
docker push your-registry/spark-pipeline:3.5.1-v1.1.0

# 2. Update SparkApplication
kubectl patch sparkapplication spark-streaming-pipeline -n spark-pipeline \
  --type=merge \
  -p '{"spec":{"image":"your-registry/spark-pipeline:3.5.1-v1.1.0"}}'

# 3. Operator will automatically restart with new image
```

### Scaling Executors Manually

```bash
# Scale up
kubectl patch sparkapplication spark-streaming-pipeline -n spark-pipeline \
  --type=merge \
  -p '{"spec":{"executor":{"instances":20}}}'

# Scale down
kubectl patch sparkapplication spark-streaming-pipeline -n spark-pipeline \
  --type=merge \
  -p '{"spec":{"executor":{"instances":5}}}'
```

### Viewing Logs

```bash
# Driver logs
kubectl logs -f -n spark-pipeline -l component=driver

# Executor logs
kubectl logs -f -n spark-pipeline -l component=executor

# All Spark logs
stern -n spark-pipeline -l app=spark-pipeline

# History server logs
kubectl logs -f -n spark-pipeline -l app=spark-history-server
```

### Debugging Performance Issues

```bash
# Check resource usage
kubectl top pods -n spark-pipeline

# View detailed metrics
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Query: rate(spark_executor_cpuTime[5m])

# Check GC overhead
# Query: rate(jvm_gc_collection_seconds_sum[5m])

# Identify bottlenecks in Spark UI
kubectl port-forward -n spark-pipeline svc/spark-ui 4040:4040
# Open Stages tab, look for slow tasks
```

### Disaster Recovery Execution

```bash
# 1. List available backups
aws s3 ls s3://spark-pipeline-backups/checkpoints/

# 2. Restore from specific backup
kubectl set env job/checkpoint-restore RESTORE_TIMESTAMP=20250101-120000 -n spark-pipeline
kubectl create job --from=job/checkpoint-restore checkpoint-restore-manual -n spark-pipeline

# 3. Wait for restore to complete
kubectl wait --for=condition=complete job/checkpoint-restore-manual -n spark-pipeline --timeout=600s

# 4. Restart SparkApplication
kubectl delete sparkapplication spark-streaming-pipeline -n spark-pipeline
kubectl apply -f 05-spark-application.yaml
```

### Maintenance Window (Node Draining)

```bash
# Cordon node to prevent new pods
kubectl cordon <node-name>

# Drain node gracefully (respects PDBs)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# PDB ensures minimum executors remain available
# Driver won't be evicted due to PDB minAvailable: 1

# After maintenance, uncordon node
kubectl uncordon <node-name>
```

---

## Troubleshooting Common Issues

### Issue: Driver Pod CrashLoopBackOff

**Diagnosis**:
```bash
kubectl describe pod <driver-pod> -n spark-pipeline
kubectl logs <driver-pod> -n spark-pipeline --previous
```

**Common Causes**:
1. Invalid S3 credentials
2. Missing checkpoint directory
3. Insufficient memory
4. Image pull failure

**Resolution**:
```bash
# Verify S3 credentials
kubectl get secret spark-s3-credentials -n spark-pipeline -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d

# Check PVC mount
kubectl get pvc -n spark-pipeline

# Increase driver memory
kubectl patch sparkapplication spark-streaming-pipeline -n spark-pipeline \
  --type=merge \
  -p '{"spec":{"driver":{"memory":"8g"}}}'
```

### Issue: Executors Stuck in Pending

**Diagnosis**:
```bash
kubectl describe pod <executor-pod> -n spark-pipeline
```

**Common Causes**:
1. Insufficient cluster resources
2. Node selector mismatch
3. PVC binding issues

**Resolution**:
```bash
# Check available nodes
kubectl get nodes

# Scale cluster
eksctl scale nodegroup --cluster=spark-pipeline --name=standard-workers --nodes=5

# Remove node selector if needed
kubectl patch sparkapplication spark-streaming-pipeline -n spark-pipeline \
  --type=json \
  -p='[{"op": "remove", "path": "/spec/executor/nodeSelector"}]'
```

### Issue: HPA Not Scaling

**Diagnosis**:
```bash
kubectl describe hpa spark-executor-hpa -n spark-pipeline
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/spark-pipeline/pods
```

**Common Causes**:
1. Metrics server not installed
2. Missing resource requests
3. Metrics not available

**Resolution**:
```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify resource requests are set (should be in 05-spark-application.yaml)
kubectl get pod <executor-pod> -n spark-pipeline -o yaml | grep -A4 requests
```

---

## Best Practices Checklist

- [ ] Use External Secrets Operator for credential management
- [ ] Enable Pod Security Standards (restricted profile)
- [ ] Configure TLS for all Spark communication
- [ ] Set up multi-AZ node placement
- [ ] Configure PodDisruptionBudgets for HA
- [ ] Enable Prometheus monitoring and alerting
- [ ] Set up automated backups (checkpoints + volumes)
- [ ] Configure resource limits on all pods
- [ ] Use NetworkPolicies for network segmentation
- [ ] Enable audit logging
- [ ] Set up log aggregation (ELK, Splunk, etc.)
- [ ] Configure Velero for cluster-level backups
- [ ] Test disaster recovery procedures quarterly
- [ ] Document runbooks for common issues
- [ ] Set up cost monitoring and alerts

---

## Next Steps

1. **Production Readiness**: Complete all items in Best Practices Checklist
2. **Performance Tuning**: Monitor metrics, adjust executor count/memory
3. **Cost Optimization**: Use spot instances for executors, tune auto-scaling
4. **Security Hardening**: Enable all security features in 09-security.yaml
5. **Disaster Recovery Testing**: Schedule quarterly DR drills

For questions or issues, refer to:
- Spark Operator Documentation: https://github.com/GoogleCloudPlatform/spark-on-k8s-operator
- Kubernetes Documentation: https://kubernetes.io/docs/
- Apache Spark Documentation: https://spark.apache.org/docs/latest/
