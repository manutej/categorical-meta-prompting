# Production Security Configuration for Spark on Kubernetes

**Version**: 1.0
**Last Updated**: 2025-12-04
**Compliance**: PCI-DSS, SOC2, HIPAA, CIS Kubernetes Benchmark

---

## Overview

This repository contains enterprise-grade security configurations for running Apache Spark data pipelines on Kubernetes. These configurations implement defense-in-depth security principles with multiple layers of protection.

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Audit & Compliance                       │
│  • API Audit Logs  • Compliance Tags  • Retention Policies  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Network Security                         │
│  • NetworkPolicy   • Egress Control   • TLS Encryption      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Secret Management                        │
│  • External Secrets  • Rotation  • Encryption at Rest       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Pod Security                             │
│  • Non-Root  • Read-Only FS  • Drop Capabilities            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RBAC & Authentication                    │
│  • ServiceAccounts  • Roles  • Least Privilege              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Kubernetes 1.28+ cluster
- `kubectl` CLI configured
- RBAC enabled
- CNI plugin with NetworkPolicy support (Calico, Cilium, or Weave)
- cert-manager (optional, for TLS automation)
- External Secrets Operator (optional, for secret management)

### Installation

1. **Apply RBAC Configuration**
   ```bash
   kubectl apply -f rbac.yaml
   ```
   Creates ServiceAccounts, Roles, and RoleBindings for Spark components.

2. **Apply Pod Security Standards**
   ```bash
   kubectl apply -f pod-security.yaml
   ```
   Enforces restricted pod security policies.

3. **Configure Secret Management**
   ```bash
   # Option A: External Secrets Operator (Recommended)
   kubectl apply -f secrets-management.yaml

   # Option B: Kubernetes Secrets (Development only)
   kubectl create secret generic spark-s3-credentials \
     --from-literal=aws-access-key-id=YOUR_KEY \
     --from-literal=aws-secret-access-key=YOUR_SECRET \
     -n spark-system
   ```

4. **Apply Network Policies**
   ```bash
   kubectl apply -f network-policy.yaml
   ```
   Establishes zero-trust network segmentation.

5. **Configure TLS/SSL** (Optional)
   ```bash
   # Install cert-manager
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

   # Apply TLS configuration
   kubectl apply -f tls-configuration.yaml
   ```

6. **Enable Audit Logging**
   ```bash
   kubectl apply -f audit-compliance.yaml
   ```

### Verification

Run the security verification script:

```bash
# Automated verification
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs -f job/kube-bench

# Manual verification
bash verify-security.sh
```

Review the [Security Checklist](SECURITY-CHECKLIST.md) for comprehensive verification.

---

## Configuration Files

### 1. RBAC Configuration (`rbac.yaml`)

**Purpose**: Implements least-privilege access control for Spark components.

**Components**:
- **ServiceAccounts**: Separate identities for operator, driver, and executor
- **Roles**: Namespace-scoped permissions
- **ClusterRoles**: Cluster-wide permissions (operator only)
- **RoleBindings**: Permission grants

**Key Features**:
- No ClusterAdmin privileges
- Resource name restrictions for secrets
- Minimal executor permissions
- AWS IRSA integration support

**Usage**:
```yaml
spec:
  driver:
    serviceAccount: spark-driver
  executor:
    serviceAccount: spark-executor
```

---

### 2. Pod Security (`pod-security.yaml`)

**Purpose**: Enforces secure pod configurations aligned with CIS Kubernetes Benchmark.

**Components**:
- **Pod Security Standards**: Namespace-level enforcement (restricted)
- **SecurityContext Templates**: Reusable security configurations
- **Resource Quotas**: Namespace resource limits
- **LimitRanges**: Default resource constraints

**Key Features**:
- Non-root user enforcement (UID 185)
- Read-only root filesystem
- Dropped capabilities (ALL)
- Seccomp profile (RuntimeDefault)
- No privilege escalation

**Usage**:
```yaml
spec:
  driver:
    podSecurityContext:
      runAsNonRoot: true
      runAsUser: 185
      fsGroup: 185
    securityContext:
      capabilities:
        drop: [ALL]
      readOnlyRootFilesystem: true
```

---

### 3. Secret Management (`secrets-management.yaml`)

**Purpose**: Secure credential management with external integration and rotation.

**Components**:
- **Kubernetes Secrets**: Basic secret storage
- **External Secrets Operator**: AWS Secrets Manager integration
- **HashiCorp Vault Integration**: Enterprise secret management
- **Sealed Secrets**: GitOps-friendly encrypted secrets
- **Secret Rotation**: Automated credential rotation

**Key Features**:
- Never store secrets in Git
- Automatic secret synchronization
- 90-day rotation policy
- Encryption at rest
- Audit trail for secret access

**Integration Patterns**:

**AWS Secrets Manager**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: spark-s3-external
spec:
  secretStoreRef:
    name: aws-secrets-manager
  data:
    - secretKey: aws-access-key-id
      remoteRef:
        key: prod/spark/s3-credentials
        property: access_key_id
```

**HashiCorp Vault**:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      auth:
        kubernetes:
          role: "spark-role"
```

---

### 4. Network Security (`network-policy.yaml`)

**Purpose**: Zero-trust network segmentation with egress control.

**Components**:
- **Default Deny**: Baseline deny-all policy
- **Operator Policy**: Spark operator communication rules
- **Driver Policy**: Driver-executor and external connectivity
- **Executor Policy**: Minimal executor network access
- **Egress Policy**: Controlled external access

**Key Features**:
- Default deny-all baseline
- Least-privilege network access
- Pod selector-based rules
- AWS metadata service blocking
- IP whitelisting for external services

**Network Flow**:
```
┌──────────────┐
│   Operator   │ ←─────── Kubernetes API Server
└──────┬───────┘
       │
       ↓
┌──────────────┐         ┌──────────────┐
│    Driver    │ ←─────→ │  Executor 1  │
└──────┬───────┘         └──────────────┘
       │                  ┌──────────────┐
       └─────────────────→│  Executor 2  │
                          └──────────────┘
       ↓                         ↓
┌─────────────────────────────────────┐
│  External: S3, Database, Kafka      │
└─────────────────────────────────────┘
```

**Validation**:
```bash
# Test driver-executor connectivity
kubectl exec -n spark-system <driver-pod> -- nc -zv <executor-pod-ip> 7078

# Test external access
kubectl exec -n spark-system <driver-pod> -- wget -O- https://s3.amazonaws.com
```

---

### 5. TLS/SSL Configuration (`tls-configuration.yaml`)

**Purpose**: End-to-end encryption for all Spark communication.

**Components**:
- **Certificate Authority**: Root CA for signing certificates
- **cert-manager Integration**: Automated certificate lifecycle
- **Driver Certificates**: TLS certificates for driver pods
- **Executor Certificates**: TLS certificates for executor pods
- **Spark TLS Configuration**: TLS settings for all Spark components

**Key Features**:
- TLS 1.3 protocol
- Strong cipher suites
- Mutual TLS (mTLS)
- Automated certificate rotation
- Hostname verification

**Encrypted Channels**:
- **RPC**: Driver-executor communication
- **Block Transfer**: Shuffle data encryption
- **Spark UI**: HTTPS for web interface
- **History Server**: Encrypted log access

**Configuration**:
```yaml
sparkConf:
  spark.ssl.enabled: "true"
  spark.ssl.rpc.enabled: "true"
  spark.ssl.protocol: "TLSv1.3"
  spark.ssl.keyStore: "/opt/spark/tls/keystore.jks"
  spark.ssl.trustStore: "/opt/spark/tls/truststore.jks"
```

**Certificate Lifecycle**:
```
┌─────────────┐
│   CA Cert   │ (90 day validity)
└──────┬──────┘
       │
       ├─────→ Driver Cert (auto-renew at 75 days)
       │
       └─────→ Executor Cert (auto-renew at 75 days)
```

---

### 6. Audit & Compliance (`audit-compliance.yaml`)

**Purpose**: Comprehensive audit logging and compliance monitoring.

**Components**:
- **Kubernetes Audit Policy**: API server audit configuration
- **Fluentd DaemonSet**: Log collection and forwarding
- **Prometheus Monitoring**: Metrics collection and alerting
- **Compliance Tags**: Resource labeling for compliance
- **Retention Policies**: 7-year retention for compliance logs

**Key Features**:
- RequestResponse logging for SparkApplications
- Metadata logging for secrets (no values)
- Centralized logging to Elasticsearch
- Long-term archival to S3 Glacier
- Compliance tag enforcement

**Audit Log Flow**:
```
Kubernetes API Server
       ↓ (audit logs)
Fluentd DaemonSet
       ↓
       ├──→ Elasticsearch (operational, 1 year)
       │
       └──→ S3 Glacier (compliance, 7 years)
```

**Compliance Standards**:
- **PCI-DSS**: Payment card industry
- **SOC2**: Service organization controls
- **HIPAA**: Healthcare data protection
- **CIS Benchmark**: Security best practices

**Alert Examples**:
- Failed Spark applications (critical)
- Unauthorized secret access (critical)
- High executor failure rate (warning)
- Network policy violations (warning)

---

## Security Checklist

The [Security Checklist](SECURITY-CHECKLIST.md) provides a comprehensive verification guide covering:

1. **Pre-Deployment Security**: Cluster baseline, image scanning
2. **RBAC Configuration**: ServiceAccounts, roles, permissions
3. **Pod Security**: SecurityContext, resource limits
4. **Secret Management**: Encryption, rotation, injection
5. **Network Security**: NetworkPolicy, egress control
6. **TLS/SSL Configuration**: Certificate management, encryption
7. **Audit and Compliance**: Logging, monitoring, alerting
8. **Runtime Security**: Falco, OPA Gatekeeper
9. **Monitoring and Alerting**: Metrics, dashboards, alerts
10. **Incident Response**: Detection, response, remediation

Use this checklist for:
- Pre-deployment validation
- Security audits
- Compliance reviews
- Incident investigations

---

## Architecture Diagrams

### Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Namespace: spark-system                       │   │
│  │                                                         │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Pod Security Standards: Restricted              │  │   │
│  │  │                                                  │  │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌───────────┐ │  │   │
│  │  │  │   Driver   │  │ Executor 1 │  │ Executor 2│ │  │   │
│  │  │  │            │  │            │  │           │ │  │   │
│  │  │  │  Non-root  │  │  Non-root  │  │ Non-root  │ │  │   │
│  │  │  │  RO rootfs │  │  RO rootfs │  │ RO rootfs │ │  │   │
│  │  │  │  TLS: Yes  │  │  TLS: Yes  │  │ TLS: Yes  │ │  │   │
│  │  │  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘ │  │   │
│  │  │        │               │               │       │  │   │
│  │  └────────┼───────────────┼───────────────┼───────┘  │   │
│  │           │               │               │          │   │
│  │  ┌────────▼───────────────▼───────────────▼───────┐  │   │
│  │  │          NetworkPolicy Enforcement            │  │   │
│  │  │  • Default Deny  • Egress Control             │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │          RBAC Authorization                    │  │   │
│  │  │  • ServiceAccounts  • Roles  • Least Privilege│  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          External Secret Management                  │   │
│  │  AWS Secrets Manager / HashiCorp Vault              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Audit Logging & Compliance                  │   │
│  │  • API Audit  • Fluentd  • Elasticsearch  • S3      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow with Security

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTPS (TLS 1.3)
       ↓
┌──────────────────┐
│  Spark Operator  │ ← ServiceAccount: spark-operator
└──────┬───────────┘   RBAC: ClusterRole (limited)
       │
       │ Creates
       ↓
┌──────────────────┐
│  Driver Pod      │ ← ServiceAccount: spark-driver
│  UID: 185        │   RBAC: Role (pod, service, configmap)
│  RO rootfs: true │   NetworkPolicy: Allow executor, S3, DB
│  TLS: Yes        │   Secrets: Injected via environment
└──────┬───────────┘
       │ Encrypted RPC (TLS 1.3)
       ↓
┌──────────────────┐
│  Executor Pods   │ ← ServiceAccount: spark-executor
│  UID: 185        │   RBAC: Role (pod read-only)
│  RO rootfs: true │   NetworkPolicy: Allow driver, shuffle
│  TLS: Yes        │   Secrets: Inherited from driver
└──────┬───────────┘
       │ Encrypted Shuffle (TLS 1.3)
       ↓
┌──────────────────┐
│  External Data   │ ← NetworkPolicy: Egress allowed
│  S3, DB, Kafka   │   Credentials: From Secrets Manager
└──────────────────┘   Connection: TLS encrypted
```

---

## Best Practices

### 1. Never Store Secrets in Git

- Use External Secrets Operator or Sealed Secrets
- Add `*.yaml` with secrets to `.gitignore`
- Scan repositories for leaked credentials

### 2. Implement Defense in Depth

- **Layer 1**: RBAC (who can do what)
- **Layer 2**: Pod Security (how pods run)
- **Layer 3**: Network Policy (what can communicate)
- **Layer 4**: TLS (encrypt all traffic)
- **Layer 5**: Audit (log everything)

### 3. Least Privilege Principle

- Grant minimal required permissions
- Use resource name restrictions for secrets
- Separate driver and executor ServiceAccounts
- No ClusterAdmin for any component

### 4. Encrypt Everything

- TLS 1.3 for all Spark communication
- etcd encryption at rest
- KMS for secret encryption
- HTTPS for external services

### 5. Monitor and Alert

- Alert on security events (unauthorized access, failures)
- Dashboard for compliance metrics
- 24/7 monitoring with on-call rotation
- Incident response procedures

### 6. Regular Security Audits

- Monthly vulnerability scans
- Quarterly penetration testing
- Annual compliance reviews
- Continuous image scanning

### 7. Automate Security

- Use cert-manager for certificate lifecycle
- Use External Secrets Operator for secret rotation
- Use OPA Gatekeeper for policy enforcement
- Use Falco for runtime security

---

## Troubleshooting

### RBAC Issues

**Problem**: Pod cannot access secrets
```bash
# Check ServiceAccount permissions
kubectl auth can-i get secrets --as=system:serviceaccount:spark-system:spark-driver -n spark-system

# Verify RBAC configuration
kubectl get role spark-driver-role -n spark-system -o yaml
kubectl get rolebinding spark-driver-rolebinding -n spark-system -o yaml
```

**Solution**: Add secret access to Role with resource names:
```yaml
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    resourceNames: ["spark-s3-credentials"]
    verbs: ["get"]
```

### Network Policy Issues

**Problem**: Driver cannot connect to executors
```bash
# Test connectivity
kubectl exec -n spark-system <driver-pod> -- nc -zv <executor-pod-ip> 7078

# Check NetworkPolicy
kubectl get networkpolicy -n spark-system
kubectl describe networkpolicy spark-driver-policy -n spark-system
```

**Solution**: Verify pod labels match NetworkPolicy selectors:
```bash
kubectl get pods -n spark-system --show-labels
```

### TLS Certificate Issues

**Problem**: Certificate not ready
```bash
# Check certificate status
kubectl get certificate -n spark-system
kubectl describe certificate spark-driver-cert -n spark-system
```

**Solution**: Check cert-manager logs and issuer configuration:
```bash
kubectl logs -n cert-manager deployment/cert-manager
kubectl get issuer spark-ca-issuer -n spark-system -o yaml
```

### Secret Access Issues

**Problem**: ExternalSecret not syncing
```bash
# Check ExternalSecret status
kubectl get externalsecret -n spark-system
kubectl describe externalsecret spark-s3-external -n spark-system
```

**Solution**: Verify SecretStore configuration and IRSA permissions:
```bash
kubectl get secretstore -n spark-system -o yaml
kubectl logs -n external-secrets-system deployment/external-secrets
```

---

## Migration Guide

### From Insecure to Secure Configuration

**Phase 1: RBAC** (Low Risk)
1. Create ServiceAccounts
2. Create Roles with current permissions
3. Update SparkApplications to use ServiceAccounts
4. Gradually reduce permissions

**Phase 2: Pod Security** (Medium Risk)
1. Test SecurityContext in staging
2. Add emptyDir volumes for writable directories
3. Update applications to run as non-root
4. Apply pod security standards

**Phase 3: Network Policy** (High Risk)
1. Create allow-all policy initially
2. Add specific allow rules
3. Test in staging thoroughly
4. Change default to deny-all
5. Monitor for blocked connections

**Phase 4: TLS** (High Risk)
1. Install cert-manager
2. Generate certificates
3. Update Spark configuration with TLS
4. Test in staging
5. Roll out to production with rollback plan

**Phase 5: Secret Management** (Medium Risk)
1. Set up External Secrets Operator
2. Migrate secrets to Secrets Manager/Vault
3. Create ExternalSecrets
4. Update applications to use new secrets
5. Delete old Kubernetes secrets

---

## Performance Impact

| Security Feature | Performance Impact | Mitigation |
|------------------|-------------------|------------|
| RBAC | Negligible (<1ms per request) | None needed |
| Pod Security | Negligible | None needed |
| NetworkPolicy | Low (1-5% overhead) | Use eBPF-based CNI (Cilium) |
| TLS Encryption | Low-Medium (5-10% CPU) | Use hardware acceleration (AES-NI) |
| Audit Logging | Low (2-5% API server) | Filter verbose logs |
| Secret Rotation | Negligible | Background process |

**Recommendations**:
- Use Cilium for lowest NetworkPolicy overhead
- Enable CPU AES-NI for TLS acceleration
- Filter audit logs to reduce volume
- Use init containers for secret fetching

---

## References

### Kubernetes Security

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)

### Spark Security

- [Apache Spark Security](https://spark.apache.org/docs/latest/security.html)
- [Spark SSL Configuration](https://spark.apache.org/docs/latest/security.html#ssl-configuration)
- [Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)

### Compliance Standards

- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/document_library)
- [SOC2 Trust Service Criteria](https://www.aicpa.org/soc)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Tools and Projects

- [cert-manager](https://cert-manager.io/)
- [External Secrets Operator](https://external-secrets.io/)
- [Falco Runtime Security](https://falco.org/)
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- [Cilium Network Policy](https://cilium.io/)

---

## Support

For questions or issues:

1. Review the [Security Checklist](SECURITY-CHECKLIST.md)
2. Check [Troubleshooting](#troubleshooting) section
3. Review Kubernetes and Spark documentation
4. Contact your security team for compliance questions

---

## License

This configuration is provided as-is for educational and production use. Adapt to your organization's specific security requirements and compliance standards.

---

**Last Updated**: 2025-12-04
**Version**: 1.0
**Maintainer**: Data Platform Team
