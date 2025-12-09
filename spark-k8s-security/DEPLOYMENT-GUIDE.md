# Spark on Kubernetes Security - Deployment Guide

**Version**: 1.0
**Deployment Time**: 30-60 minutes
**Prerequisites**: Kubernetes 1.28+, kubectl, helm (optional)

---

## Overview

This guide walks through deploying the complete security configuration for Spark on Kubernetes in the correct order to avoid issues.

---

## Pre-Deployment Checklist

Before you begin, ensure:

- [ ] Kubernetes cluster is running (1.28+)
- [ ] `kubectl` is configured and working
- [ ] You have cluster-admin permissions
- [ ] CNI with NetworkPolicy support is installed (Calico, Cilium, Weave)
- [ ] You have reviewed the security requirements
- [ ] You have obtained necessary credentials for external services

### Verify Prerequisites

```bash
# Kubernetes version
kubectl version --short
# Required: v1.28.0 or higher

# RBAC enabled
kubectl api-versions | grep rbac.authorization.k8s.io
# Should show: rbac.authorization.k8s.io/v1

# NetworkPolicy support
kubectl get crd networkpolicies.networking.k8s.io
# Should succeed

# Check your permissions
kubectl auth can-i '*' '*'
# Should return: yes
```

---

## Step-by-Step Deployment

### Step 1: Create Namespace (5 minutes)

```bash
# Create the namespace with Pod Security Standards
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: spark-system
  labels:
    name: spark-system
    environment: production
    compliance: required
    cost-center: data-engineering

    # Pod Security Standards
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
EOF

# Verify namespace
kubectl get ns spark-system -o yaml
```

**Verification**:
```bash
kubectl get ns spark-system -o jsonpath='{.metadata.labels}' | grep pod-security
```

---

### Step 2: Deploy RBAC Configuration (10 minutes)

```bash
# Apply RBAC configuration
kubectl apply -f rbac.yaml

# Wait for resources to be created
kubectl wait --for=condition=Complete --timeout=60s \
  -n spark-system \
  serviceaccount/spark-operator

# Verify ServiceAccounts
kubectl get sa -n spark-system
# Should show: spark-operator, spark-driver, spark-executor

# Verify Roles
kubectl get role,rolebinding -n spark-system

# Verify ClusterRoles (for operator)
kubectl get clusterrole,clusterrolebinding | grep spark
```

**Verification**:
```bash
# Check permissions for spark-driver
kubectl auth can-i get pods \
  --as=system:serviceaccount:spark-system:spark-driver \
  -n spark-system
# Should return: yes

# Verify no cluster-admin
kubectl auth can-i '*' '*' \
  --as=system:serviceaccount:spark-system:spark-driver
# Should return: no
```

---

### Step 3: Configure Secret Management (15 minutes)

Choose one of the following options:

#### Option A: Kubernetes Secrets (Development/Testing)

```bash
# Create S3 credentials secret
kubectl create secret generic spark-s3-credentials \
  --from-literal=aws-access-key-id='YOUR_ACCESS_KEY' \
  --from-literal=aws-secret-access-key='YOUR_SECRET_KEY' \
  --from-literal=aws-region='us-east-1' \
  -n spark-system

# Create database credentials secret
kubectl create secret generic spark-database-credentials \
  --from-literal=jdbc-url='jdbc:postgresql://postgres.example.com:5432/analytics' \
  --from-literal=jdbc-username='spark_user' \
  --from-literal=jdbc-password='YOUR_PASSWORD' \
  -n spark-system

# Verify secrets
kubectl get secrets -n spark-system
```

#### Option B: External Secrets Operator (Production - Recommended)

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace \
  --set installCRDs=true

# Wait for deployment
kubectl wait --for=condition=Available \
  deployment/external-secrets \
  -n external-secrets-system \
  --timeout=300s

# Apply secret management configuration
kubectl apply -f secrets-management.yaml

# Verify ExternalSecrets are syncing
kubectl get externalsecret -n spark-system
kubectl describe externalsecret spark-s3-external -n spark-system
```

**Verification**:
```bash
# Check if secrets exist
kubectl get secrets -n spark-system

# Verify secret has correct keys (without showing values)
kubectl get secret spark-s3-credentials -n spark-system -o jsonpath='{.data}' | jq 'keys'
```

---

### Step 4: Apply Pod Security Standards (5 minutes)

```bash
# Apply pod security configuration
kubectl apply -f pod-security.yaml

# Verify ResourceQuota
kubectl get resourcequota -n spark-system
kubectl describe resourcequota spark-quota -n spark-system

# Verify LimitRange
kubectl get limitrange -n spark-system
kubectl describe limitrange spark-limits -n spark-system
```

**Verification**:
```bash
# Test: Try to create privileged pod (should be rejected)
kubectl run test-privileged \
  --image=nginx \
  --privileged \
  -n spark-system
# Should fail with pod security violation

# Clean up
kubectl delete pod test-privileged -n spark-system --ignore-not-found
```

---

### Step 5: Deploy Network Policies (10 minutes)

```bash
# Apply network policies
kubectl apply -f network-policy.yaml

# Verify all policies are created
kubectl get networkpolicy -n spark-system
# Should show: default-deny-all, allow-dns, spark-operator-policy,
#              spark-driver-policy, spark-executor-policy, spark-egress-external

# Describe default deny policy
kubectl describe networkpolicy default-deny-all -n spark-system
```

**Verification**:
```bash
# Test DNS resolution (should work)
kubectl run test-dns \
  --image=busybox \
  --rm -it \
  --labels=app=spark \
  -n spark-system \
  -- nslookup google.com
# Should resolve successfully

# Test external access without proper labels (should fail after default deny)
kubectl run test-external \
  --image=busybox \
  --rm -it \
  -n spark-system \
  -- wget -O- --timeout=5 http://example.com
# Should timeout (blocked by default deny)
```

---

### Step 6: Configure TLS/SSL (15 minutes - Optional but Recommended)

#### Install cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=Available \
  deployment/cert-manager \
  -n cert-manager \
  --timeout=300s

kubectl wait --for=condition=Available \
  deployment/cert-manager-webhook \
  -n cert-manager \
  --timeout=300s

# Verify installation
kubectl get pods -n cert-manager
```

#### Apply TLS Configuration

```bash
# Apply TLS configuration
kubectl apply -f tls-configuration.yaml

# Wait for certificates to be ready
kubectl wait --for=condition=Ready \
  certificate/spark-driver-cert \
  -n spark-system \
  --timeout=120s

kubectl wait --for=condition=Ready \
  certificate/spark-executor-cert \
  -n spark-system \
  --timeout=120s

# Verify certificates
kubectl get certificate -n spark-system
kubectl describe certificate spark-driver-cert -n spark-system
```

**Verification**:
```bash
# Check certificate secrets were created
kubectl get secret spark-driver-tls-auto -n spark-system
kubectl get secret spark-executor-tls-auto -n spark-system

# Verify certificate validity
kubectl get certificate spark-driver-cert -n spark-system \
  -o jsonpath='{.status.notAfter}'
```

---

### Step 7: Enable Audit Logging (10 minutes)

```bash
# Install Fluentd for log collection
kubectl apply -f audit-compliance.yaml

# Verify Fluentd is running
kubectl get daemonset -n kube-system | grep fluentd

# Verify Prometheus monitoring
kubectl get servicemonitor -n spark-system
kubectl get prometheusrule -n spark-system
```

**Verification**:
```bash
# Check Fluentd logs
kubectl logs -n kube-system daemonset/fluentd --tail=50

# Verify Prometheus scraping configuration
kubectl get servicemonitor spark-metrics -n spark-system -o yaml
```

---

### Step 8: Deploy Spark Operator (Optional)

If you're using Spark Operator:

```bash
# Install Spark Operator using Helm
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update

helm install spark-operator spark-operator/spark-operator \
  --namespace spark-system \
  --set serviceAccounts.spark.name=spark-operator \
  --set webhook.enable=true \
  --set enableBatchScheduler=true

# Wait for operator to be ready
kubectl wait --for=condition=Available \
  deployment/spark-operator \
  -n spark-system \
  --timeout=300s

# Verify operator
kubectl get deployment spark-operator -n spark-system
kubectl logs -n spark-system deployment/spark-operator
```

---

### Step 9: Test with Sample SparkApplication

```bash
# Apply the secure Spark example from pod-security.yaml
kubectl apply -f - <<EOF
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi-secure
  namespace: spark-system
spec:
  type: Scala
  mode: cluster
  image: "spark:3.5.0"
  imagePullPolicy: IfNotPresent
  mainClass: org.apache.spark.examples.SparkPi
  mainApplicationFile: "local:///opt/spark/examples/jars/spark-examples_2.12-3.5.0.jar"
  sparkVersion: "3.5.0"

  restartPolicy:
    type: OnFailure
    onFailureRetries: 3

  driver:
    cores: 1
    memory: "2048m"
    serviceAccount: spark-driver
    labels:
      app: spark-pi
      component: driver

  executor:
    cores: 1
    instances: 2
    memory: "2048m"
    serviceAccount: spark-executor
    labels:
      app: spark-pi
      component: executor
EOF

# Watch the application
kubectl get sparkapplication -n spark-system -w

# Check driver pod
kubectl get pods -n spark-system -l spark-role=driver

# View logs
kubectl logs -n spark-system -l spark-role=driver
```

**Verification**:
```bash
# Check application completed successfully
kubectl get sparkapplication spark-pi-secure -n spark-system \
  -o jsonpath='{.status.applicationState.state}'
# Should show: COMPLETED

# Verify security context was applied
kubectl get pod -n spark-system -l spark-role=driver \
  -o jsonpath='{.items[0].spec.securityContext}'
```

---

### Step 10: Final Security Verification

```bash
# Run the security verification script
cat > verify-deployment.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Spark on Kubernetes Security Deployment Verification ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
check_pass() {
  echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
  echo -e "${RED}✗${NC} $1"
}

# Check namespace
echo "1. Checking namespace..."
if kubectl get ns spark-system &>/dev/null; then
  check_pass "Namespace 'spark-system' exists"
else
  check_fail "Namespace 'spark-system' does not exist"
fi

# Check RBAC
echo "2. Checking RBAC..."
SA_COUNT=$(kubectl get sa -n spark-system | grep spark | wc -l | tr -d ' ')
if [ "$SA_COUNT" -ge 3 ]; then
  check_pass "ServiceAccounts configured ($SA_COUNT found)"
else
  check_fail "ServiceAccounts missing (expected 3, found $SA_COUNT)"
fi

# Check secrets
echo "3. Checking secrets..."
SECRET_COUNT=$(kubectl get secrets -n spark-system | grep spark | wc -l | tr -d ' ')
if [ "$SECRET_COUNT" -ge 1 ]; then
  check_pass "Secrets configured ($SECRET_COUNT found)"
else
  check_fail "No secrets found"
fi

# Check NetworkPolicies
echo "4. Checking NetworkPolicies..."
NP_COUNT=$(kubectl get networkpolicy -n spark-system 2>/dev/null | wc -l | tr -d ' ')
if [ "$NP_COUNT" -ge 5 ]; then
  check_pass "NetworkPolicies configured ($NP_COUNT found)"
else
  check_fail "NetworkPolicies missing (expected 5+, found $NP_COUNT)"
fi

# Check default deny
if kubectl get networkpolicy default-deny-all -n spark-system &>/dev/null; then
  check_pass "Default deny policy exists"
else
  check_fail "Default deny policy missing"
fi

# Check certificates (if cert-manager is used)
echo "5. Checking TLS certificates..."
if kubectl get certificate -n spark-system &>/dev/null 2>&1; then
  CERT_COUNT=$(kubectl get certificate -n spark-system | wc -l | tr -d ' ')
  check_pass "Certificates configured ($CERT_COUNT found)"
else
  echo "  ℹ Certificates not configured (optional)"
fi

# Check resource quotas
echo "6. Checking resource quotas..."
if kubectl get resourcequota -n spark-system &>/dev/null; then
  check_pass "ResourceQuota configured"
else
  check_fail "ResourceQuota not configured"
fi

# Check limit ranges
if kubectl get limitrange -n spark-system &>/dev/null; then
  check_pass "LimitRange configured"
else
  check_fail "LimitRange not configured"
fi

# Check pod security
echo "7. Checking Pod Security Standards..."
PSS=$(kubectl get ns spark-system -o jsonpath='{.metadata.labels.pod-security\.kubernetes\.io/enforce}')
if [ "$PSS" == "restricted" ]; then
  check_pass "Pod Security Standards enforced (restricted)"
else
  check_fail "Pod Security Standards not enforced"
fi

echo ""
echo "=== Verification Complete ==="
EOF

chmod +x verify-deployment.sh
./verify-deployment.sh
```

---

## Post-Deployment Tasks

### 1. Configure Monitoring Alerts

```bash
# Verify Prometheus is scraping Spark metrics
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Navigate to http://localhost:9090/targets and verify spark-system targets

# Check alert rules
kubectl get prometheusrule -n spark-system -o yaml
```

### 2. Set Up Log Forwarding

```bash
# Verify Fluentd is forwarding logs
kubectl logs -n kube-system daemonset/fluentd --tail=100

# Check Elasticsearch indices
kubectl port-forward -n logging svc/elasticsearch 9200:9200
curl http://localhost:9200/_cat/indices | grep spark
```

### 3. Document Configuration

```bash
# Generate documentation of deployed resources
kubectl get all,networkpolicy,certificate,externalsecret -n spark-system -o yaml > deployed-config.yaml

# Save current state
kubectl get ns spark-system -o yaml > namespace-config.yaml
kubectl get sa,role,rolebinding -n spark-system -o yaml > rbac-config.yaml
```

### 4. Test Failover and Rollback

```bash
# Create backup of current configuration
kubectl get all -n spark-system -o yaml > backup-$(date +%Y%m%d).yaml

# Test rollback procedure
# (Keep this backup for disaster recovery)
```

---

## Rollback Procedure

If something goes wrong:

```bash
# Rollback network policies (if blocking legitimate traffic)
kubectl delete networkpolicy --all -n spark-system
# Then re-apply selectively

# Rollback pod security (if pods won't start)
kubectl label namespace spark-system pod-security.kubernetes.io/enforce-
# Then fix pod configurations and re-enable

# Rollback TLS (if connectivity issues)
kubectl delete certificate --all -n spark-system
# Update SparkApplications to disable TLS temporarily

# Complete rollback
kubectl delete namespace spark-system
# Then start over from Step 1
```

---

## Troubleshooting

### Issue: Pods won't start due to Pod Security

**Symptoms**: Pods in `CrashLoopBackOff` or `CreateContainerError`

**Solution**:
```bash
# Check pod events
kubectl describe pod -n spark-system <pod-name>

# Common fixes:
# 1. Add emptyDir volumes for writable directories
# 2. Ensure runAsUser is non-root (185)
# 3. Set readOnlyRootFilesystem: true
# 4. Drop all capabilities
```

### Issue: Network Policy blocking legitimate traffic

**Symptoms**: Timeout errors, connection refused

**Solution**:
```bash
# Test connectivity
kubectl exec -n spark-system <pod> -- nc -zv <target-ip> <port>

# Check pod labels
kubectl get pods -n spark-system --show-labels

# Verify NetworkPolicy selectors match labels
kubectl get networkpolicy -n spark-system -o yaml | grep -A 5 podSelector
```

### Issue: Secrets not accessible

**Symptoms**: Authentication errors, missing credentials

**Solution**:
```bash
# Check RBAC permissions
kubectl auth can-i get secrets \
  --as=system:serviceaccount:spark-system:spark-driver \
  -n spark-system

# Verify secret exists
kubectl get secret spark-s3-credentials -n spark-system

# Check ExternalSecret status (if using ESO)
kubectl describe externalsecret -n spark-system
```

---

## Next Steps

After successful deployment:

1. Review the [Security Checklist](SECURITY-CHECKLIST.md) for ongoing verification
2. Set up regular security audits (monthly)
3. Configure backup and disaster recovery
4. Train team on security procedures
5. Document any customizations
6. Schedule periodic security reviews

---

## Support

For issues during deployment:

1. Review this guide's troubleshooting section
2. Check the main [README.md](README.md) for additional documentation
3. Review Kubernetes and Spark logs
4. Contact your security team for compliance questions

---

**Deployment Complete!**

Your Spark on Kubernetes environment is now secured with:
- ✓ RBAC with least privilege
- ✓ Pod Security Standards (restricted)
- ✓ Network isolation with NetworkPolicy
- ✓ Secret management with encryption
- ✓ TLS/SSL for all communication (optional)
- ✓ Comprehensive audit logging
- ✓ Resource quotas and limits
- ✓ Compliance monitoring and alerting
