# Apache Spark on Kubernetes Self-Healing Patterns - Comprehensive Research

## Executive Summary

This document provides comprehensive research on building self-healing Apache Spark data pipelines on Kubernetes, covering Spark Operator patterns, self-healing mechanisms, Kubernetes-native resilience, observability stacks, and chaos testing approaches. The research focuses on Spark 3.x/4.x and Kubernetes 1.28+ environments.

**Key Findings:**
- Spark 3.0+ introduces native Kubernetes support with improved failure recovery mechanisms
- The Kubeflow Spark Operator (v1beta2) provides declarative application management with automated restart policies
- Graceful decommissioning (Spark 3.1+) enables robust handling of executor failures and spot instance interruptions
- Native Prometheus support (Spark 3.0+) simplifies monitoring without external dependencies
- Chaos engineering tools (LitmusChaos, Chaos Mesh) enable proactive resilience testing

---

## Table of Contents

1. [Spark Operator Patterns](#1-spark-operator-patterns)
2. [Self-Healing Mechanisms](#2-self-healing-mechanisms)
3. [Kubernetes-Native Resilience](#3-kubernetes-native-resilience)
4. [Observability Stack](#4-observability-stack)
5. [Chaos Testing Approaches](#5-chaos-testing-approaches)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Best Practices Summary](#7-best-practices-summary)
8. [References](#references)

---

## 1. Spark Operator Patterns

### 1.1 Spark Operator Architecture

The [Kubeflow Spark Operator](https://github.com/kubeflow/spark-operator) is a Kubernetes operator for managing the lifecycle of Apache Spark applications on Kubernetes. It is currently in beta status at API version **v1beta2**.

**Core Architecture:**
- Uses Kubernetes CustomResourceDefinitions (CRDs) for declarative application specification
- Watches SparkApplication and ScheduledSparkApplication resources across namespaces
- Automatically executes `spark-submit` on behalf of users for eligible applications
- Leverages mutating admission webhooks for advanced pod customization

**Compatibility:**
- Kubernetes: 1.16+
- Spark: 2.3 and above (latest v2.3.x uses Spark 4.0.0)
- Helm: 3+

### 1.2 SparkApplication CRD Specification

The SparkApplication CRD is the primary interface for running Spark workloads on Kubernetes.

**Key Specifications:**

```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: spark-pi
  namespace: default
spec:
  type: Scala
  mode: cluster
  image: spark:4.0.0
  imagePullPolicy: Always
  mainClass: org.apache.spark.examples.SparkPi
  mainApplicationFile: local:///opt/spark/examples/jars/spark-examples.jar

  sparkVersion: "4.0.0"

  # Restart policy for self-healing
  restartPolicy:
    type: OnFailure
    onFailureRetries: 3
    onFailureRetryInterval: 10
    onSubmissionFailureRetries: 5
    onSubmissionFailureRetryInterval: 20

  # Driver configuration
  driver:
    cores: 1
    coreLimit: "1200m"
    memory: "512m"
    labels:
      version: "4.0.0"
    serviceAccount: spark

  # Executor configuration
  executor:
    cores: 1
    instances: 2
    memory: "512m"
    labels:
      version: "4.0.0"
```

**API Migration Note:**
Users on `v1beta1` must migrate to `v1beta2` by:
1. Deleting existing CRDs: `sparkapplications.sparkoperator.k8s.io` and `scheduledsparkapplications.sparkoperator.k8s.io`
2. Installing the latest operator version or applying `config/crd/bases`

### 1.3 Driver and Executor Pod Management

**Pod Lifecycle:**

According to [Apache Spark documentation](https://spark.apache.org/docs/latest/running-on-kubernetes.html):

1. **Driver Pod Creation**: "Spark creates a Spark driver running within a Kubernetes pod"
2. **Executor Management**: The driver launches executor pods and maintains connections to coordinate work
3. **Resource Cleanup**: When applications complete, executor pods terminate immediately, while the driver pod persists in "completed" state until garbage collection

**Graceful Shutdown (Client Mode):**
Setting `spark.kubernetes.driver.pod.name` enables garbage collection through OwnerReferences, ensuring executor pods are automatically deleted when the driver pod is removed.

**Pod Persistence Behavior:**
If network requests to the API server fail during executor cleanup, pods may remain in the cluster. However, "the executor processes should exit when they cannot reach the driver," preventing ongoing resource consumption.

### 1.4 Restart Policies and Failure Recovery

The Spark Operator provides **automatic application restart with configurable policies**:

**Restart Policy Types:**

1. **Never**: No automatic restart (default for some configurations)
2. **OnFailure**: Restart only on application failure
3. **Always**: Restart regardless of exit status

**Configuration Parameters:**

```yaml
restartPolicy:
  type: OnFailure
  onFailureRetries: 3              # Max retries on failure
  onFailureRetryInterval: 10       # Seconds between retries
  onSubmissionFailureRetries: 5    # Max retries for submission failures
  onSubmissionFailureRetryInterval: 20  # Seconds between submission retries
```

**Retry with Linear Back-off:**
The operator supports "automatic retries of failed submissions with optional linear back-off," reducing thundering herd effects during cluster-wide issues.

**Limitations:**
According to [SPARK-30055](https://issues.apache.org/jira/browse/SPARK-30055), "The current Kubernetes scheduler hard-codes the restart policy for all pods to be 'Never'." To restart a failed application, all pods must be deleted and rescheduled, which is slow and clears any caches.

---

## 2. Self-Healing Mechanisms

### 2.1 Automatic Driver Restart Strategies

**Driver Failure Recovery:**

The Spark driver is responsible for overall application management. From the [Apache Spark Kubernetes documentation](https://spark.apache.org/docs/latest/running-on-kubernetes.html):

- The driver "communicates directly with the Kubernetes API to request resources for executors and manage their lifecycle"
- It "orchestrates task execution, monitors progress, and handles failure recovery"

**Recommended Configuration for Driver Resilience:**

```properties
# Enable driver restart via Spark Operator
restartPolicy.type=OnFailure
restartPolicy.onFailureRetries=3
restartPolicy.onFailureRetryInterval=30

# Driver memory overhead for stability
spark.kubernetes.memoryOverheadFactor=0.1

# Service account with appropriate permissions
spark.kubernetes.authenticate.driver.serviceAccountName=spark-driver
```

**Known Issues:**
[SPARK-37999](https://www.mail-archive.com/issues@spark.apache.org/msg306561.html) documents an issue where "Spark executors self-exit due to driver disassociation in Kubernetes" with error "Executor self-exiting due to: Driver disassociated! Shutting down."

### 2.2 Executor Failure Recovery

**Native Spark Recovery:**

Spark provides built-in executor failure tolerance:
- Failed tasks are automatically retried on healthy executors
- Task failures don't count against maximum failures during graceful decommissioning
- Dynamic allocation can spawn replacement executors

**Graceful Executor Decommissioning (Spark 3.1+):**

From [Data Mechanics blog](https://www.datamechanics.co/blog/apache-spark-3-1-release-spark-on-kubernetes-is-now-ga):

This feature "makes Spark a lot more robust and performant when working with spot nodes, ensuring that before the spot interruption occurs, the shuffle and cache data is moved so that the Spark application can continue with minimal impact."

**Decommissioning Behavior:**
- Executor marked for decommissioning is blacklisted - no new tasks scheduled
- Running tasks are not forcibly interrupted
- Failed tasks are retried elsewhere without counting against failure threshold
- Shuffle files and cached data migrate to remaining executors
- Fallback to object store (S3) if no other executors available

**Configuration:**

```properties
# Enable graceful decommissioning
spark.decommission.enabled=true

# Decommission script path
spark.kubernetes.executor.decommissionScript=/opt/decom.sh

# Label for pod disruption budgets
spark.kubernetes.executor.decommissionLabel=decommission

# Executor roll policy options: ID, ADD_TIME, TOTAL_GC_TIME, TOTAL_DURATION, OUTLIER
spark.kubernetes.executor.rollPolicy=OUTLIER

# Minimum tasks before rolling
spark.kubernetes.executor.minTasksPerExecutorBeforeRolling=10
```

### 2.3 Checkpointing for Structured Streaming

From [Cisco Outshift blog](https://outshift.cisco.com/blog/spark-checkpointing) and [Medium articles](https://medium.com/@alonisser/spark-structured-streaming-checkpointing-2dbb2b2afdd0):

**Checkpoint Fundamentals:**

"Checkpoints are the 'identity' and 'state' of your stream." They enable:
- Recovery from driver failures
- Exactly-once processing semantics
- State restoration after restarts

**Storage Options for Kubernetes:**

1. **Cloud Object Storage** (S3, GCS, Azure Blob):
   - Most common for Kubernetes
   - Avoid managing HDFS clusters
   - Note: S3 is slow for large applications

2. **Managed File Systems**:
   - **AWS EFS**: Better performance than S3
   - **Azure Files**: Persistent shared storage
   - **GCP Persistent Disk**: With GCS connector

3. **Kubernetes Persistent Volumes**:
   - Use PVCs for local checkpoint storage
   - Better performance than object storage
   - Requires proper volume lifecycle management

**Configuration Example:**

```scala
df.writeStream
  .format("parquet")
  .option("checkpointLocation", "gs://spark-checkpoint-location/app1")
  .option("path", "gs://output-location/")
  .start()
```

**Best Practices:**

From [Stack Overflow discussions](https://stackoverflow.com/questions/62799984/spark-structured-streaming-checkpoint-usage-in-production):

1. **Separate directories per query**: Each streaming query needs its own checkpoint folder
2. **Write checkpoints to write stream only**: Setting checkpoints in read stream is redundant
3. **Schema consistency**: State schema must remain constant across restarts - no schema modifications allowed
4. **Avoid checkpoint changes**: Changes in number/type of input sources not allowed between restarts

**Kubernetes Operator Integration:**

"Kubernetes takes care of failing Spark executors and drivers by restarting failing pods. Although this is enough for executors, for a driver it is necessary, but insufficient. In order to make such a driver more resilient to failure, Spark checkpointing must first be enabled."

**Object Store Challenges:**

From [Qubole blog](https://www.qubole.com/blog/structured-streaming-with-direct-write-checkpointing):

"One of the most frequent issues with Structured Streaming was related to reliability when running it in a cloud environment, with some object store (usually S3) as checkpoint location. A Streaming Application would often crash with a File Not Found exception."

Solution: Direct Write Checkpointing - tasks write checkpoint data directly to final file instead of temporary files.

### 2.4 Write-Ahead Logs (WAL) Configuration

**WAL Overview:**

From [Databricks blog](https://www.databricks.com/blog/2015/01/15/improved-driver-fault-tolerance-and-zero-data-loss-in-spark-streaming.html) and [WaitingForCode](https://www.waitingforcode.com/apache-spark-streaming/spark-streaming-checkpointing-and-write-ahead-logs/read):

"If enabled, all the data received from a receiver gets written into a write-ahead log in the configuration checkpoint directory. This prevents data loss on driver recovery, thus ensuring zero data loss."

**WAL in Spark Streaming (Legacy):**

```properties
# Enable WAL for receivers
spark.streaming.receiver.writeAheadLog.enable=true

# Checkpoint directory (HDFS or S3)
spark.streaming.checkpoint.directory=hdfs://namenode:port/checkpoint
```

**WAL in Structured Streaming:**

From [Stack Overflow](https://stackoverflow.com/questions/60385591/location-of-wal-in-spark-structured-streaming):

"In Spark Structured Streaming, there is no WAL with every message from the receiver. Only two logs with metadata for every batch: offset and commit logs."

**Implementation Details:**

"Structured Streaming uses the Write-Ahead Log (WAL) to capture ingested data that has been received, but not yet processed by a query. If a failure occurs and processing is restarted from the WAL, any events received from the source aren't lost."

The WAL is a "write-ahead-log that records the offsets that are present in each batch. In order to ensure that a given batch will always consist of the same data, we write to this log *before* any processing is done."

**Performance Considerations:**

From [Apache Spark documentation](https://spark.apache.org/docs/latest/streaming-programming-guide.html):

"These stronger semantics may come at the cost of the receiving throughput of individual receivers. This can be corrected by running more receivers in parallel to increase aggregate throughput."

**Important Note:**
It is recommended to disable replication when WAL is enabled: "the replication of the received data within Spark be disabled when the write-ahead log is enabled as the log is already stored in a replicated storage system."

### 2.5 Shuffle Data Recovery

From [Apache Spark Kubernetes documentation](https://spark.apache.org/docs/latest/running-on-kubernetes.html):

**Feature:** Shuffle data persistence through `KubernetesLocalDiskShuffleDataIO` plugin (Spark 3.4+)

**Configuration:**

```properties
# Enable shuffle data recovery
spark.shuffle.sort.io.plugin.class=org.apache.spark.shuffle.KubernetesLocalDiskShuffleDataIO

# Wait to reuse PVCs across executor replacements
spark.kubernetes.driver.waitToReusePersistentVolumeClaim=true

# Enable shuffle tracking (required for dynamic allocation without external shuffle service)
spark.dynamicAllocation.shuffleTracking.enabled=true
```

**PVC Requirements:**
- Configure persistent volume claims with names starting with `spark-local-dir-`
- PVCs store shuffle data that persists across executor failures
- Driver can reuse volumes when spawning replacement executors

**Dynamic Allocation Integration:**

"For stage-level scheduling with dynamic allocation, enable shuffle tracking since Kubernetes lacks external shuffle services."

---

## 3. Kubernetes-Native Resilience

### 3.1 Liveness and Readiness Probe Patterns

From [Kubernetes documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/):

**Probe Types:**

1. **Startup Probes**: Check whether a container has started
2. **Readiness Probes**: Check whether a container is ready to handle requests
3. **Liveness Probes**: Check whether a container is still running normally

**How They Work:**

- **Readiness**: "Is this Pod ready to handle requests?" Failed probes stop traffic but keep pod running
- **Liveness**: "Is this Pod still working?" Failed probes trigger pod restart
- **Startup**: Delays liveness/readiness checks until application starts

**Spark-Specific Configuration:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spark-driver
spec:
  containers:
  - name: spark
    image: spark:4.0.0
    ports:
    - containerPort: 4040
      name: spark-ui

    # Startup probe - allow long initialization
    startupProbe:
      httpGet:
        path: /
        port: 4040
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 30  # 5 minutes total

    # Liveness probe - restart if UI becomes unresponsive
    livenessProbe:
      httpGet:
        path: /
        port: 4040
      initialDelaySeconds: 120
      periodSeconds: 30
      failureThreshold: 3
      timeoutSeconds: 10

    # Readiness probe - traffic only when ready
    readinessProbe:
      httpGet:
        path: /
        port: 4040
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
```

**Key Configuration Parameters:**

- **initialDelaySeconds**: Seconds after container start before probes begin (critical for Spark's long startup)
- **periodSeconds**: How often to perform the probe (default: 10s, minimum: 1s)
- **failureThreshold**: Consecutive failures before considering probe failed (default: 3)
- **timeoutSeconds**: Seconds before probe times out (default: 1s)

**Best Practices:**

From [GroundCover](https://www.groundcover.com/blog/kubernetes-liveness-probe) and [Kubernetes.io](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/):

1. **Different endpoints**: Use `/health/live` for liveness and `/health/ready` for readiness
2. **Higher failure threshold for liveness**: Ensure pod is observed as not-ready before hard kill
3. **Account for startup time**: Spark drivers/executors need significant `initialDelaySeconds` (60-120s)
4. **Use exec probes for process checks**: Alternative to HTTP probes for verifying Spark process

**Executor Probe Example:**

```yaml
executor:
  livenessProbe:
    exec:
      command:
      - /bin/sh
      - -c
      - "ps aux | grep 'org.apache.spark.executor.CoarseGrainedExecutorBackend' | grep -v grep"
    initialDelaySeconds: 60
    periodSeconds: 30
    failureThreshold: 3
```

### 3.2 PodDisruptionBudget Configuration

From [Kubernetes documentation](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) and [best practices guides](https://teckbootcamps.medium.com/kubernetes-pod-disruption-budget-the-practical-guide-2024-d35cc0ae06c3):

**Purpose:**
PDBs ensure minimum availability during voluntary disruptions (node maintenance, upgrades, scaling).

**Configuration Options:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: spark-executor-pdb
spec:
  minAvailable: 2  # or use maxUnavailable
  selector:
    matchLabels:
      spark-role: executor
      spark-app-selector: spark-streaming-app
```

**Key Parameters:**

1. **minAvailable**: Minimum pods that must remain available (number or percentage)
2. **maxUnavailable**: Maximum pods that can be unavailable (number or percentage)

**Note:** You can specify only one of `maxUnavailable` and `minAvailable` per PDB.

**Best Practices for Spark:**

1. **Avoid zero voluntary evictions**: Don't set `maxUnavailable: 0` or `minAvailable: 100%` - prevents node draining
2. **Use AlwaysAllow unhealthy pod eviction**: Set `unhealthyPodEvictionPolicy: AlwaysAllow` to evict misbehaving pods
3. **Percentage-based values**: Use percentages for flexibility as deployments scale
4. **Align with SLOs**: Set realistic constraints matching application availability requirements
5. **Separate PDBs for driver and executors**: Different policies for different roles

**Spark Driver PDB Example:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: spark-driver-pdb
spec:
  maxUnavailable: 0  # Never allow driver disruption during voluntary events
  selector:
    matchLabels:
      spark-role: driver
  unhealthyPodEvictionPolicy: AlwaysAllow
```

**Spark Executor PDB Example:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: spark-executor-pdb
spec:
  minAvailable: 50%  # Keep at least half of executors during maintenance
  selector:
    matchLabels:
      spark-role: executor
  unhealthyPodEvictionPolicy: AlwaysAllow
```

**Integration with Graceful Decommissioning:**

From [Spark documentation](https://spark.apache.org/docs/latest/running-on-kubernetes.html):

Use `spark.kubernetes.executor.decommissionLabel` to label executors for PDB coordination during decommissioning.

### 3.3 HorizontalPodAutoscaler for Executors

From [blog posts](https://blog.madhukaraphatak.com/horizontal-scaling-k8s-part-3) and [Medium articles](https://domisj.medium.com/first-steps-with-apache-spark-on-k8s-standalone-spark-auto-scaling-with-hpa-327f858f453b):

**Scaling Approaches:**

1. **Spark Dynamic Resource Allocation (DRA)**: Horizontal scaling at the Spark application level
2. **Kubernetes HorizontalPodAutoscaler (HPA)**: Horizontal scaling at the pod level
3. **Vertical Pod Autoscaler (VPA)**: Vertical scaling of pod resources

**How HPA Works with Spark:**

"The Horizontal Pod Autoscaler automatically scales the number of pods in a replication controller, deployment or replica set based on observed CPU utilization."

**Integration Pattern:**

"The dynamic allocation mode of Spark starts with a minimum number of executors. But as more tasks are scheduled, it will start requesting more executors. This in turn should request more resources from Kubernetes which will kick in the auto scaling."

**DRA Configuration:**

```properties
# Enable dynamic resource allocation
spark.dynamicAllocation.enabled=true
spark.dynamicAllocation.shuffleTracking.enabled=true

# Allocation bounds
spark.dynamicAllocation.minExecutors=2
spark.dynamicAllocation.maxExecutors=10
spark.dynamicAllocation.initialExecutors=2

# Scaling behavior
spark.dynamicAllocation.executorIdleTimeout=60s
spark.dynamicAllocation.schedulerBacklogTimeout=1s
```

**HPA Configuration Example:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: spark-executor-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: spark-executor-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
```

**Important Considerations:**

From [AWS blog](https://aws.amazon.com/blogs/big-data/improve-reliability-and-reduce-costs-of-your-apache-spark-workloads-with-vertical-autoscaling-on-amazon-emr-on-eks/):

"Vertical autoscaling complements existing Spark autoscaling solutions such as Dynamic Resource Allocation (DRA) and Kubernetes autoscaling solutions such as Karpenter."

**Challenges:**

From [Outshift blog](https://outshift.cisco.com/blog/scaling-spark-k8s):

"Kubernetes autoscalers do re-balance the executor pods to increase node utilization by killing pods on lightly loaded nodes. However, you may need to disable re-balancing by setting safe-to-evict = false since Kubernetes is not aware of the Spark shuffle data and cached dataframes."

**Recommendation:**
"While Kubernetes should handle node additions and removals, it's best if executor (pod) level auto-scaling decisions are handled at the Spark layer" via DRA.

**GCP Spark Operator Dynamic Allocation:**

```yaml
spec:
  dynamicAllocation:
    enabled: true
    initialExecutors: 2
    minExecutors: 2
    maxExecutors: 10
```

### 3.4 Resource Requests/Limits Best Practices

From [Stackable documentation](https://docs.stackable.tech/home/stable/spark-k8s/usage-guide/resources/) and [Kubernetes docs](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/):

**Spark-Specific Configuration:**

`spark.kubernetes.{driver,executor}.{request|limit}.cores` determines the actual pod CPU request and is taken directly from the manifest.

**Task Parallelism:**
"Task parallelism (the number of tasks an executor can run concurrently) is determined by `spark.executor.cores`."

**Memory Overhead:**
"Memory values for `spark.{driver|executor}.memory` are passed to Spark in such a way that overheads added by Spark are already implicitly declared: this overhead is applied using a factor of 0.1 (JVM jobs) or 0.4 (non-JVM jobs), being not less than 384MB."

**Resource Management Fundamentals:**

From [Kubernetes documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/):

- **Requests**: kube-scheduler uses requests to decide node placement
- **Limits**: kubelet enforces limits - container cannot exceed limit
- **CPU Throttling**: CPU limits enforced by restricting access - soft limit
- **OOM Kills**: Memory limits enforced by terminating container - hard limit

**Best Practices:**

From [PerfectScale](https://www.perfectscale.io/blog/kubernetes-cpu-limit-best-practises) and [NashTech](https://blog.nashtechglobal.com/best-practices-of-resource-requests-and-limits-in-kubernetes/):

1. **Avoid CPU Limits for Performance-Critical Apps**:
   "CPU limits are not effective for preventing noisy neighbors or protecting nodes from overallocation. Instead, they prevent the use of idle CPU resources, leading to wasted capacity."

2. **Set CPU Requests, Not Limits**:
   "It's actually CPU requests, not limits, that ensure a minimum amount of CPU for your workloads."

3. **Memory Limits Are Critical**:
   "Unlike CPU resources, memory cannot be compressed. Because there is no way to throttle memory usage, if a container goes past its memory limit it will be terminated."

4. **Keep CPU at '1' or Below**:
   "Unless your app is specifically designed to take advantage of multiple cores, it is usually a best practice to keep the CPU request at '1' or below, and run more replicas to scale it out."

5. **Use Percentage-Based Overhead**:
   Set `spark.kubernetes.memoryOverheadFactor` appropriately (default 0.1 for JVM, 0.4 for non-JVM)

**Spark Configuration Example:**

```yaml
driver:
  cores: 1
  coreRequest: "1000m"    # 1 CPU core requested
  # No coreLimit set to avoid throttling
  memory: "2g"
  memoryOverhead: "512m"  # Or use memoryOverheadFactor

executor:
  cores: 2
  coreRequest: "2000m"    # 2 CPU cores requested
  # No coreLimit set to avoid throttling
  memory: "4g"
  memoryOverhead: "1g"
  instances: 3
```

**Namespace-Level Resource Control:**

From [Kubernetes documentation](https://kubernetes.io/docs/concepts/policy/resource-quotas/):

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: spark-quota
  namespace: spark-apps
spec:
  hard:
    requests.cpu: "100"
    requests.memory: "200Gi"
    limits.memory: "300Gi"
    pods: "50"
```

---

## 4. Observability Stack

### 4.1 Prometheus Metrics Exposure from Spark

From [DZLab articles](https://dzlab.github.io/bigdata/2020/07/03/spark3-monitoring-2/) and [Kubeflow documentation](https://www.kubeflow.org/docs/components/spark-operator/user-guide/monitoring-with-jmx-and-prometheus/):

**Native Prometheus Support (Spark 3.0+):**

"Apache Spark 3.0 brings native support for monitoring with Prometheus in Kubernetes."

**Key Advantage:**
"The advantages of PrometheusServlet vs JmxSink & JmxExporter are clear: dependency elimination on the external JAR, reusing of the existing port that has been used in Spark already for monitoring, taking advantage of Prometheus Service Discovery in Kubernetes."

**Configuration Parameters:**

```properties
# Enable Prometheus metrics endpoint
spark.ui.prometheus.enabled=true

# Kubernetes annotations for Prometheus scraping
spark.kubernetes.driver.annotation.prometheus.io/scrape=true
spark.kubernetes.driver.annotation.prometheus.io/path=/metrics/executors/prometheus/
spark.kubernetes.driver.annotation.prometheus.io/port=4040

# Same for executors
spark.kubernetes.executor.annotation.prometheus.io/scrape=true
spark.kubernetes.executor.annotation.prometheus.io/path=/metrics/prometheus/
spark.kubernetes.executor.annotation.prometheus.io/port=4040
```

**Metrics Endpoint:**

"The Spark driver exposes metrics through a dedicated endpoint" at `http://localhost:4040/metrics/executors/prometheus/`

**Alternative: JMX Exporter Approach (Spark 2.x):**

From [Kubeflow documentation](https://www.kubeflow.org/docs/components/spark-operator/user-guide/monitoring-with-jmx-and-prometheus/):

"Spark Operator supports exporting Spark metrics in Prometheus format using the JMX Prometheus Exporter."

**JMX Configuration:**

```yaml
monitoring:
  exposeDriverMetrics: true
  exposeExecutorMetrics: true
  prometheus:
    jmxExporterJar: "/prometheus/jmx_prometheus_javaagent-0.19.0.jar"
    port: 8090
    configFile: "/prometheus/metrics.properties"
```

### 4.2 Important Metrics to Monitor

From [various blog posts](https://dzlab.github.io/data/2020/06/08/monitoring-spark-prometheus/):

**Resource Utilization:**
- Number of cores
- CPU time
- Memory used (HEAP and OFF-HEAP)
- Maximum memory allocated
- Disk used

**Spark Tasks:**
- Number of active/failed/completed tasks
- Task max/average/min duration
- Task input/output sizes

**Spark Streaming:**
- Number of receivers
- Number of running/failed/completed batches
- Number of records received/processed
- Average record processing time
- Processing delay
- Scheduling delay

**JVM Metrics:**
- Garbage collection time and count
- Thread count
- Class loading statistics

**Executor Metrics:**
- Executor failures
- Executor additions/removals (dynamic allocation)
- Shuffle read/write sizes
- Cache hit/miss rates

### 4.3 ServiceMonitor Configuration

From [DZLab article](https://dzlab.github.io/bigdata/2020/07/03/spark3-monitoring-2/):

**Prometheus Operator Integration:**

"Prometheus discovery requires a Kubernetes `ServiceMonitor` object."

**ServiceMonitor Example:**

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: spark-application-monitor
  namespace: spark-apps
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      spark-role: driver
  endpoints:
  - port: spark-ui
    path: /metrics/executors/prometheus/
    interval: 5s
    scheme: http
```

**Prerequisites:**
- Prometheus Operator installed (via Helm: `kube-prometheus-stack`)
- Service objects for Spark driver/executors with appropriate labels
- RBAC permissions for ServiceMonitor

**Service Creation:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: spark-driver-svc
  labels:
    spark-role: driver
    spark-app-selector: my-spark-app
spec:
  ports:
  - port: 4040
    targetPort: 4040
    name: spark-ui
  selector:
    spark-role: driver
    spark-app-selector: my-spark-app
```

**Push vs Pull Model:**

From [monitoring guides](https://itnext.io/monitoring-spark-streaming-on-k8s-with-prometheus-and-grafana-e6d8720c4a02):

"Pushing the metrics to Prometheus is a best practice for batch jobs."

For batch jobs, use Prometheus Pushgateway:

```properties
spark.metrics.conf.driver.sink.prometheus.class=org.apache.spark.metrics.sink.PrometheusPushGatewaySink
spark.metrics.conf.driver.sink.prometheus.pushgateway-address=pushgateway:9091
spark.metrics.conf.driver.sink.prometheus.period=5
```

### 4.4 Grafana Dashboard Patterns

From [Grafana Labs](https://grafana.com/grafana/dashboards/7890-spark-performance-metrics/) and [GitHub repositories](https://github.com/cerndb/spark-dashboard):

**Official Grafana Dashboards:**

1. **Spark Performance Metrics Dashboard** (ID: 7890)
   - Driver/Executor Memory Consumption
   - Network I/O metrics
   - Disk Read/Write metrics
   - Works with JMX Exporter and Prometheus Service Discovery

2. **Spark-Operator Scale Test Dashboard** (ID: 23032)
   - Operator performance metrics
   - Kubernetes resource utilization
   - Uses gauge, piechart, and timeseries panels

3. **Apache Spark JMX Metrics Dashboard** (ID: 23304)
   - Real-time executor and driver performance
   - Memory usage visualization
   - Garbage collection metrics
   - Thread activity monitoring
   - Job statistics

**CERN Spark Dashboard:**

From [GitHub - cerndb/spark-dashboard](https://github.com/cerndb/spark-dashboard):

"Spark-Dashboard is a solution for monitoring Apache Spark jobs. This repository provides the tooling and configuration for deploying an Apache Spark Performance Dashboard using containers technology."

**Features:**
- Works with Spark 4.x and 3.x
- Supports Hadoop, Kubernetes, and Spark Standalone
- Pre-built Docker images available
- Comprehensive performance visualization

**Installation:**

```bash
# Import dashboard JSON into Grafana
# Dashboard available at: https://github.com/cerndb/spark-dashboard/blob/master/dashboards/spark-dashboard.json
```

**Grafana Cloud Integration:**

From [Grafana documentation](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/integrations/integration-reference/integration-spark/):

"The Grafana Cloud integration includes 1 pre-built dashboard to help monitor and visualize Apache Spark metrics. This integration monitors a Spark cluster based on the built-in Prometheus plugin, available from version 3.0 upwards."

### 4.5 Spark UI Integration on Kubernetes

From [blog posts](https://www.jacobsalway.com/blog/using-spark-operator-with-nginx-ingress-controller) and [GitHub repositories](https://github.com/lmouhib/auto-register-spark-ui-k8s):

**Challenge:**
"With a service alone, the UI is only accessible from inside the cluster. You must then create an Ingress to expose the UI outside the cluster."

**Approach 1: Spark Operator UI Service/Ingress**

Configuration in Helm values:

```yaml
controller:
  uiService:
    enable: true
  uiIngress:
    enable: true
    urlFormat: /{{$appNamespace}}/{{$appName}}
```

Install with:

```bash
helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --values spark-values.yaml
```

**Approach 2: Auto-Register Spark UI Controller**

From [GitHub - lmouhib/auto-register-spark-ui-k8s](https://github.com/lmouhib/auto-register-spark-ui-k8s):

"The Auto Register Spark UI controller operates by utilizing a Kubernetes informer to listen for newly created services within the cluster. It specifically filters these services to identify those associated with Spark applications by checking for a predefined Spark application selector."

**Supported Ingress Controllers:**
- NGINX
- Traefik

**Approach 3: Reverse Proxy (EMR on EKS Pattern)**

From [AWS EMR documentation](https://aws.github.io/aws-emr-containers-best-practices/troubleshooting/docs/reverse-proxy-sparkui/):

"A reverse proxy sits between a single Ingress ALB and multiple driver pods. The ALB forwards all incoming traffic to the reverse proxy, which then directs requests to the appropriate driver pods based on the URI path in each request."

**Manual Ingress Configuration:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spark-ui-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: spark-ui.example.com
    http:
      paths:
      - path: /spark-app-1
        pathType: Prefix
        backend:
          service:
            name: spark-app-1-driver-svc
            port:
              number: 4040
```

**Important Configuration:**

"For the UI to be effectively accessible through the Ingress, you must set up HTTP redirection with an alternative root path. The UI itself must be aware of this redirection by setting `spark.ui.proxyBase` to this root path."

```properties
spark.ui.proxyBase=/spark-app-1
```

**Hostname-Based Routing:**

"The operation proposed by the Spark Operator, with routing based on hostname wildcards (for example `*.ingress.cluster.com`), would overcome the problem of HTTP redirect."

---

## 5. Chaos Testing Approaches

### 5.1 Chaos Engineering Overview

From [LitmusChaos](https://litmuschaos.io/) and [comparison articles](https://blog.container-solutions.com/comparing-chaos-engineering-tools):

**Purpose:**
Chaos engineering helps teams "identify infrastructure weaknesses through safe, controlled chaos tests" before issues impact production systems.

**Key Categories:**
1. **Chaos Orchestrators**: LitmusChaos, Chaos Toolkit
2. **Chaos Injectors**: Chaos Mesh, Pumba

### 5.2 LitmusChaos

From [LitmusChaos website](https://litmuschaos.io/) and [CNCF blog](https://www.cncf.io/blog/2024/03/19/chaos-engineering-in-2024-with-litmuschaos/):

**Overview:**

"LitmusChaos is a CNCF-incubating platform designed to help teams identify infrastructure vulnerabilities through controlled chaos testing."

**Adoption:**
- 30+ million Docker pulls
- 500+ companies using/trying the platform
- Active community support via CNCF Slack
- Presented at KubeCon + CloudNativeCon North America 2024

**Key Features:**

1. **ChaosHub**: Repository of pre-tested, tunable chaos experiments
2. **Declarative Experiments**: Chain experiments sequentially or in parallel
3. **Litmus Probes**: Validate steady-state hypotheses during failures
4. **Chaos Observability**: Export Prometheus metrics, integrate with APM tools

**Installation:**

```bash
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm install litmus litmuschaos/litmus --namespace litmus --create-namespace
```

**2024 Updates:**

From [CNCF blog](https://www.cncf.io/blog/2024/03/19/chaos-engineering-in-2024-with-litmuschaos/):

**Version 3.1.0:**
- Stop Experiment feature for greater control over chaos injections
- Ability to halt ongoing experiments to mitigate unforeseen consequences

**Version 3.4.0:**
- Integration with OSS Fuzz for continuous fuzz testing
- Identifies vulnerabilities and weaknesses in codebase
- Proactively addresses security threats

### 5.3 Chaos Mesh

From [Medium article](https://medium.com/@DevopsFollower/testing-the-resilience-of-your-kubernetes-systems-using-chaos-mesh-65fa5a2b2989) and [comparison blogs](https://www.vcluster.com/blog/analyzing-five-popular-chaos-engineering-platforms):

**Overview:**

"Chaos Mesh is a chaos platform made exclusively for Kubernetes applications. It was created by PingCap to test the resilience of their distributed database TiDB."

**Key Features:**
- Web UI: Chaos Dashboard
- Native Kubernetes CRD-based management
- Supports various fault simulation types:
  - Network latency
  - System time manipulation
  - Resource utilization
  - Pod failures
  - Kernel faults

**Comparison with LitmusChaos:**

"LitmusChaos is another CNCF hosted competitor. Much like Chaos Mesh, Litmus Chaos is also an open-source, cloud-native project that uses CRDs for chaos management, and is built for Kubernetes."

**Installation:**

```bash
kubectl apply -f https://mirrors.chaos-mesh.org/latest/crd.yaml
kubectl apply -f https://mirrors.chaos-mesh.org/latest/chaos-mesh.yaml
```

### 5.4 Spark-Specific Chaos Scenarios

**Pod Kill Scenarios:**

Test executor failure recovery:

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: spark-executor-kill
  namespace: spark-apps
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - spark-apps
    labelSelectors:
      spark-role: executor
  scheduler:
    cron: "@every 5m"
```

**Driver Failure Test:**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: spark-driver-kill
  namespace: spark-apps
spec:
  action: pod-failure
  mode: one
  selector:
    namespaces:
      - spark-apps
    labelSelectors:
      spark-role: driver
  duration: "30s"
```

**Network Partition Testing:**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: spark-network-partition
  namespace: spark-apps
spec:
  action: partition
  mode: all
  selector:
    namespaces:
      - spark-apps
    labelSelectors:
      spark-role: executor
  direction: both
  duration: "60s"
```

**Network Latency Injection:**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: spark-network-delay
  namespace: spark-apps
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - spark-apps
    labelSelectors:
      spark-role: executor
  delay:
    latency: "500ms"
    correlation: "50"
    jitter: "100ms"
  duration: "5m"
```

**Resource Stress Testing:**

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: spark-memory-stress
  namespace: spark-apps
spec:
  mode: one
  selector:
    namespaces:
      - spark-apps
    labelSelectors:
      spark-role: executor
  stressors:
    memory:
      workers: 4
      size: 1GB
  duration: "3m"
```

### 5.5 Recovery Validation Methodology

**Test Scenarios for Spark on Kubernetes:**

1. **Executor Pod Kill**
   - **Expected**: New executor spawned, tasks redistributed, job continues
   - **Validate**: Check job completion, metrics continuity, data integrity

2. **Driver Pod Failure**
   - **Expected**: Driver restarts (if restart policy configured), application recovers from checkpoint
   - **Validate**: Streaming query resumes from last checkpoint, no data loss

3. **Network Partition**
   - **Expected**: Executor heartbeat failures detected, executors replaced
   - **Validate**: Job completion within SLA, task retry counts

4. **Resource Exhaustion**
   - **Expected**: OOM kills trigger pod restarts, graceful degradation
   - **Validate**: Resource limits enforced, pods restart successfully

5. **Persistent Storage Failure**
   - **Expected**: Shuffle data recovery from PVCs, checkpoint recovery
   - **Validate**: No shuffle data loss, streaming state recovered

**Validation Steps:**

```bash
# 1. Baseline metrics before chaos
kubectl exec -it prometheus-pod -- curl localhost:9090/api/v1/query?query=spark_driver_BlockManager_memory_memUsed_MB

# 2. Inject chaos
kubectl apply -f chaos-experiment.yaml

# 3. Monitor recovery
kubectl get pods -n spark-apps -w
kubectl logs -n spark-apps spark-driver-pod -f

# 4. Verify metrics after recovery
# Check for:
# - Job completion
# - Task retry counts
# - Memory/CPU recovery
# - Checkpoint progression (streaming)

# 5. Validate data integrity
# Compare output data before/after chaos
```

**Automated Recovery Testing with Litmus:**

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: spark-resilience-test
  namespace: spark-apps
spec:
  appinfo:
    appns: spark-apps
    applabel: 'spark-role=driver'
  engineState: 'active'
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CHAOS_INTERVAL
              value: '10'
            - name: FORCE
              value: 'false'
        probe:
          - name: check-driver-health
            type: httpProbe
            mode: Continuous
            runProperties:
              probeTimeout: 5
              interval: 5
              retry: 3
            httpProbe/inputs:
              url: http://spark-driver-svc:4040
              method:
                get:
                  criteria: ==
                  responseCode: "200"
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Objective**: Set up basic self-healing infrastructure

**Tasks:**
1. Install Spark Operator (v1beta2)
   ```bash
   helm install spark-operator spark-operator/spark-operator \
     --namespace spark-operator \
     --create-namespace \
     --set webhook.enable=true
   ```

2. Configure basic SparkApplication with restart policy
   - Set `restartPolicy.type=OnFailure`
   - Configure retry parameters

3. Set up Prometheus Operator
   ```bash
   helm install prometheus prometheus-community/kube-prometheus-stack \
     --namespace monitoring \
     --create-namespace
   ```

4. Enable Spark metrics exposure
   - Add Prometheus annotations to SparkApplications
   - Verify metrics endpoint accessibility

**Deliverables:**
- Spark Operator running and healthy
- First SparkApplication with self-healing
- Basic Prometheus scraping configured

### Phase 2: Advanced Self-Healing (Week 3-4)

**Objective**: Implement comprehensive failure recovery mechanisms

**Tasks:**
1. Configure checkpointing for Structured Streaming
   - Set up persistent storage (PVC or cloud storage)
   - Test checkpoint recovery

2. Enable shuffle data recovery
   - Configure PVCs with `spark-local-dir-` prefix
   - Set `KubernetesLocalDiskShuffleDataIO` plugin

3. Implement graceful decommissioning
   - Enable decommissioning features
   - Configure executor roll policies

4. Set up liveness/readiness probes
   - Add HTTP probes to driver pods
   - Configure appropriate timeouts and thresholds

5. Create PodDisruptionBudgets
   - Separate PDBs for drivers and executors
   - Align with availability requirements

**Deliverables:**
- Streaming applications survive driver failures
- Executors handle spot instance interruptions gracefully
- PDBs prevent availability violations during maintenance

### Phase 3: Observability (Week 5-6)

**Objective**: Comprehensive monitoring and alerting

**Tasks:**
1. Configure ServiceMonitors for Prometheus
   - Create ServiceMonitors for drivers and executors
   - Verify metric collection

2. Import Grafana dashboards
   - Install CERN Spark Dashboard
   - Import official Grafana Labs dashboards (7890, 23032, 23304)

3. Set up Spark UI Ingress
   - Configure Nginx Ingress Controller
   - Enable Spark Operator UI service/ingress

4. Create alerting rules
   - Driver/executor failure alerts
   - Memory pressure alerts
   - Job latency alerts
   - Checkpoint lag alerts (streaming)

5. Integrate with APM (optional)
   - Connect to Datadog/New Relic/Dynatrace
   - Set up distributed tracing

**Deliverables:**
- Grafana dashboards showing real-time metrics
- Alerting to on-call team
- Spark UI accessible externally

### Phase 4: Resilience Testing (Week 7-8)

**Objective**: Validate self-healing under chaos conditions

**Tasks:**
1. Install LitmusChaos or Chaos Mesh
   ```bash
   helm install litmus litmuschaos/litmus --namespace litmus --create-namespace
   ```

2. Create chaos experiments
   - Pod kill scenarios
   - Network partition tests
   - Resource stress tests

3. Run automated recovery validation
   - Executor failure → recovery
   - Driver failure → recovery
   - Network issues → recovery

4. Document failure scenarios and recovery times
   - RTO (Recovery Time Objective)
   - RPO (Recovery Point Objective)

5. Tune configurations based on chaos results
   - Adjust timeouts
   - Refine resource limits
   - Optimize checkpoint intervals

**Deliverables:**
- Chaos test suite
- Recovery validation reports
- Tuned production configurations

### Phase 5: Production Hardening (Week 9-10)

**Objective**: Optimize for production workloads

**Tasks:**
1. Implement resource quotas and limits
   - Namespace-level ResourceQuotas
   - Per-pod resource constraints

2. Configure HPA/VPA for dynamic scaling
   - Enable Spark Dynamic Allocation
   - Set up cluster autoscaling (Karpenter/Cluster Autoscaler)

3. Security hardening
   - RBAC policies
   - Network policies
   - Pod security standards

4. Backup and disaster recovery
   - Checkpoint backup to multiple regions
   - Runbook documentation

5. Performance optimization
   - Tune Spark configurations
   - Optimize shuffle performance
   - Review memory overhead factors

**Deliverables:**
- Production-ready cluster configuration
- Security compliance documentation
- Disaster recovery runbook
- Performance tuning guide

---

## 7. Best Practices Summary

### Self-Healing Configuration

1. **Always configure restart policies**:
   ```yaml
   restartPolicy:
     type: OnFailure
     onFailureRetries: 3
     onFailureRetryInterval: 30
   ```

2. **Enable checkpointing for all streaming applications**:
   - Use reliable storage (S3, EFS, GCS)
   - Separate checkpoint directories per query
   - Test recovery regularly

3. **Configure graceful decommissioning** (Spark 3.1+):
   ```properties
   spark.decommission.enabled=true
   spark.kubernetes.executor.decommissionScript=/opt/decom.sh
   spark.kubernetes.executor.rollPolicy=OUTLIER
   ```

4. **Enable shuffle data recovery** (Spark 3.4+):
   ```properties
   spark.shuffle.sort.io.plugin.class=org.apache.spark.shuffle.KubernetesLocalDiskShuffleDataIO
   spark.kubernetes.driver.waitToReusePersistentVolumeClaim=true
   ```

### Kubernetes Resilience

1. **Add health probes to all pods**:
   - Startup probes: Long `initialDelaySeconds` (60-120s)
   - Liveness probes: High `failureThreshold` to avoid false positives
   - Readiness probes: Sensitive to application state

2. **Use PodDisruptionBudgets**:
   - Driver: `maxUnavailable: 0` (never disrupt)
   - Executors: `minAvailable: 50%` (maintain capacity)

3. **Set resource requests, avoid CPU limits**:
   - Requests: Guarantee minimum resources
   - Memory limits: Required to prevent OOM
   - CPU limits: Avoid for performance (causes throttling)

4. **Use Dynamic Resource Allocation**:
   ```properties
   spark.dynamicAllocation.enabled=true
   spark.dynamicAllocation.shuffleTracking.enabled=true
   spark.dynamicAllocation.minExecutors=2
   spark.dynamicAllocation.maxExecutors=20
   ```

### Observability

1. **Enable native Prometheus metrics** (Spark 3.0+):
   ```properties
   spark.ui.prometheus.enabled=true
   spark.kubernetes.driver.annotation.prometheus.io/scrape=true
   spark.kubernetes.driver.annotation.prometheus.io/path=/metrics/executors/prometheus/
   spark.kubernetes.driver.annotation.prometheus.io/port=4040
   ```

2. **Use ServiceMonitors for automatic discovery**:
   - Configure Prometheus Operator
   - Create ServiceMonitors matching driver/executor labels

3. **Import pre-built Grafana dashboards**:
   - Spark Performance Metrics (ID: 7890)
   - CERN Spark Dashboard (GitHub)
   - Spark Operator Scale Test (ID: 23032)

4. **Monitor critical metrics**:
   - Executor failures and additions
   - Task retry counts
   - Memory pressure (HEAP/OFF-HEAP)
   - Checkpoint lag (streaming)
   - GC time

### Chaos Testing

1. **Start with pod kill scenarios**:
   - Test executor replacement
   - Validate task retry logic

2. **Progress to driver failures**:
   - Verify checkpoint recovery
   - Validate restart policies

3. **Test network disruptions**:
   - Partition executor from driver
   - Inject latency between pods

4. **Automate recovery validation**:
   - Use Litmus probes
   - Verify data integrity
   - Measure recovery times

5. **Run chaos regularly**:
   - GameDays (quarterly)
   - Automated chaos (weekly)
   - Performance regression testing (per release)

### Version-Specific Notes

**Spark 3.0:**
- Native Prometheus support
- Structured Streaming improvements

**Spark 3.1:**
- Graceful decommissioning for Kubernetes
- Dynamic PVC allocation

**Spark 3.4:**
- `KubernetesLocalDiskShuffleDataIO` for shuffle recovery

**Spark 4.0:**
- Latest operator (v2.3.x) support
- Improved Kubernetes native scheduler

**Kubernetes 1.28+:**
- Enhanced PodDisruptionBudget policies
- Improved autoscaling algorithms
- Better probe configuration options

---

## References

### Spark Operator
- [Kubeflow Spark Operator GitHub](https://github.com/kubeflow/spark-operator)
- [Spark Operator User Guide](https://kubeflow.github.io/spark-operator/docs/user-guide.html)
- [Getting Started with Spark Operator](https://www.kubeflow.org/docs/components/spark-operator/getting-started/)

### Apache Spark on Kubernetes
- [Running Spark on Kubernetes - Official Documentation](https://spark.apache.org/docs/latest/running-on-kubernetes.html)
- [Apache Spark 3.1 Release - Spark on Kubernetes GA](https://www.datamechanics.co/blog/apache-spark-3-1-release-spark-on-kubernetes-is-now-ga)
- [SPARK-30055: Configurable Restart Policy](https://issues.apache.org/jira/browse/SPARK-30055)

### Checkpointing and Streaming
- [Spark Streaming Checkpointing on Kubernetes - Cisco Outshift](https://outshift.cisco.com/blog/spark-checkpointing)
- [Spark Structured Streaming - Fault Tolerance](https://teepika-r-m.medium.com/fault-tolerance-in-spark-structured-streaming-6463c95e32cd)
- [Using Cloud Storage for Checkpoint Location](https://jaceklaskowski.github.io/spark-kubernetes-book/demo/using-cloud-storage-for-checkpoint-location-in-spark-structured-streaming-on-google-kubernetes-engine/)
- [Spark Streaming Checkpointing and Write-Ahead Logs](https://www.waitingforcode.com/apache-spark-streaming/spark-streaming-checkpointing-and-write-ahead-logs/read)

### Kubernetes Resilience
- [Configure Liveness, Readiness and Startup Probes - Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Specifying a Disruption Budget - Kubernetes](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [Pod Disruption Budgets: The Practical Guide 2024](https://teckbootcamps.medium.com/kubernetes-pod-disruption-budget-the-practical-guide-2024-d35cc0ae06c3)
- [Resource Management for Pods and Containers - Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes CPU Limits: Best Practices](https://www.perfectscale.io/blog/kubernetes-cpu-limit-best-practises)

### Autoscaling
- [Auto Scaling Spark in Kubernetes - Part 3](https://blog.madhukaraphatak.com/horizontal-scaling-k8s-part-3)
- [First Steps with Apache Spark on K8s - Auto Scaling with HPA](https://domisj.medium.com/first-steps-with-apache-spark-on-k8s-standalone-spark-auto-scaling-with-hpa-327f858f453b)
- [Optimizing Spark Performance on Kubernetes - AWS](https://aws.amazon.com/blogs/containers/optimizing-spark-performance-on-kubernetes/)

### Monitoring and Observability
- [Spark 3.0 Monitoring with Prometheus in Kubernetes](https://dzlab.github.io/bigdata/2020/07/03/spark3-monitoring-2/)
- [Monitoring Apache Spark with Prometheus on Kubernetes - Cisco Outshift](https://outshift.cisco.com/blog/spark-monitoring)
- [Monitoring Spark Applications with Prometheus and JMX - Kubeflow](https://www.kubeflow.org/docs/components/spark-operator/user-guide/monitoring-with-jmx-and-prometheus/)
- [Apache Spark - Performance Metrics - Grafana Dashboard](https://grafana.com/grafana/dashboards/7890-spark-performance-metrics/)
- [CERN Spark Dashboard - GitHub](https://github.com/cerndb/spark-dashboard)

### Spark UI Ingress
- [Using Spark Operator with NGINX Ingress Controller](https://www.jacobsalway.com/blog/using-spark-operator-with-nginx-ingress-controller)
- [Auto Register Spark UI on Kubernetes - GitHub](https://github.com/lmouhib/auto-register-spark-ui-k8s)
- [Connect to Spark UI via Reverse Proxy - EMR Containers](https://aws.github.io/aws-emr-containers-best-practices/troubleshooting/docs/reverse-proxy-sparkui/)

### Chaos Engineering
- [LitmusChaos - Open Source Chaos Engineering Platform](https://litmuschaos.io/)
- [Chaos Engineering in 2024 with LitmusChaos - CNCF](https://www.cncf.io/blog/2024/03/19/chaos-engineering-in-2024-with-litmuschaos/)
- [Testing Resilience with Chaos Mesh](https://medium.com/@DevopsFollower/testing-the-resilience-of-your-kubernetes-systems-using-chaos-mesh-65fa5a2b2989)
- [Comparing Chaos Engineering Tools for Kubernetes](https://blog.container-solutions.com/comparing-chaos-engineering-tools)
- [Building Resilience with Chaos Engineering and Litmus](https://www.infracloud.io/blogs/building-resilience-chaos-engineering-litmus/)

---

## Appendix: Quick Reference Commands

### Spark Operator Installation

```bash
# Add Helm repository
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

# Install operator
helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --create-namespace \
  --set webhook.enable=true
```

### Submit SparkApplication

```bash
# Create SparkApplication
kubectl apply -f spark-application.yaml

# Check status
kubectl get sparkapplication -n spark-apps

# View logs
kubectl logs -n spark-apps spark-pi-driver -f

# Describe application
kubectl describe sparkapplication -n spark-apps spark-pi
```

### Monitoring Commands

```bash
# Port-forward Prometheus
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090

# Port-forward Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80

# Query metrics
curl "http://localhost:9090/api/v1/query?query=spark_driver_BlockManager_memory_memUsed_MB"

# Port-forward Spark UI
kubectl port-forward -n spark-apps svc/spark-driver-svc 4040:4040
```

### Chaos Testing Commands

```bash
# Install LitmusChaos
helm install litmus litmuschaos/litmus --namespace litmus --create-namespace

# Apply chaos experiment
kubectl apply -f chaos-experiment.yaml

# Check chaos result
kubectl get chaosresult -n spark-apps

# Delete chaos experiment
kubectl delete chaosexperiment pod-delete -n litmus
```

### Debug Commands

```bash
# Check pod events
kubectl describe pod -n spark-apps spark-driver-pod

# View executor logs
kubectl logs -n spark-apps -l spark-role=executor --tail=100

# Check resource usage
kubectl top pods -n spark-apps

# Verify PVC status
kubectl get pvc -n spark-apps

# Check ServiceMonitor
kubectl get servicemonitor -n spark-apps
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-04
**Applicable Spark Versions**: 3.0, 3.1, 3.4, 4.0
**Applicable Kubernetes Versions**: 1.28+
