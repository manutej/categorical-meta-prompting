# Self-Healing Apache Spark Data Pipeline Architecture on Kubernetes

**Version**: 1.0
**Status**: Design Phase [D]
**Last Updated**: 2025-12-04

---

## Executive Summary

This document defines a production-ready, self-healing Apache Spark data pipeline architecture deployed on Kubernetes. The design prioritizes:

- **Resilience**: Automatic recovery from failures at every layer
- **Exactly-once semantics**: Guaranteed data processing integrity
- **Elastic scalability**: Adaptive resource allocation based on load
- **Observability**: Comprehensive monitoring and alerting
- **Operational simplicity**: Declarative configuration and GitOps-ready

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Medallion Architecture (Bronze → Silver → Gold)](#2-medallion-architecture)
3. [Recovery Flow Design](#3-recovery-flow-design)
4. [Backpressure Handling](#4-backpressure-handling)
5. [High Availability Design](#5-high-availability-design)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [Configuration Patterns](#7-configuration-patterns)
8. [Self-Healing Mechanisms](#8-self-healing-mechanisms)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Monitoring & Observability](#10-monitoring--observability)

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER (Multi-Zone)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         INGESTION LAYER                               │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Kafka (3 replicas)  │  S3 Buckets  │  External APIs  │  CDC Streams  │  │
│  │      (Zone A,B,C)    │  (Raw Data)  │   (REST/gRPC)   │   (Debezium)  │  │
│  └────────┬─────────────┴──────┬───────┴────────┬────────┴──────┬────────┘  │
│           │                     │                │                │           │
│           v                     v                v                v           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    BRONZE LAYER (Raw Ingestion)                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Spark Structured Streaming Jobs (Real-time) + Batch Jobs (Hourly)   │  │
│  │  • Schema validation                • Dead letter queues              │  │
│  │  • Deduplication                    • Checkpointing (S3)              │  │
│  │  • Raw data persistence (Delta)     • Exactly-once semantics          │  │
│  │                                                                        │  │
│  │  [Pod 1: Kafka→Delta] [Pod 2: S3→Delta] [Pod 3: API→Delta]           │  │
│  │     (Replicas: 2)        (Replicas: 2)      (Replicas: 1)             │  │
│  └────────┬──────────────────────┬──────────────────────┬────────────────┘  │
│           │                       │                      │                   │
│           v                       v                      v                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              SILVER LAYER (Cleaned & Enriched)                        │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Spark Batch Jobs (every 15min) + Streaming Jobs (continuous)        │  │
│  │  • Data quality checks          • Data type conversions               │  │
│  │  • Business rule validation     • Enrichment (lookups, joins)         │  │
│  │  • PII masking/tokenization     • Partitioning optimization           │  │
│  │  • Incremental processing       • CDC merge operations                │  │
│  │                                                                        │  │
│  │  [Job 1: Cleansing] [Job 2: Enrichment] [Job 3: Quality Gates]       │  │
│  │     (Replicas: 3)       (Replicas: 2)         (Replicas: 2)           │  │
│  └────────┬──────────────────────┬──────────────────────┬────────────────┘  │
│           │                       │                      │                   │
│           v                       v                      v                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                GOLD LAYER (Business Aggregates)                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Spark Batch Jobs (scheduled) + Materialized Views                   │  │
│  │  • Complex aggregations         • Business metrics                    │  │
│  │  • Machine learning features    • Reporting datasets                  │  │
│  │  • Time-series rollups          • SLA tracking                        │  │
│  │  • Multi-dimensional cubes      • Slowly changing dimensions          │  │
│  │                                                                        │  │
│  │  [Job 1: Aggregates] [Job 2: ML Features] [Job 3: Reports]           │  │
│  │     (Replicas: 2)        (Replicas: 1)         (Replicas: 1)          │  │
│  └────────┬──────────────────────┬──────────────────────┬────────────────┘  │
│           │                       │                      │                   │
│           v                       v                      v                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       SERVING LAYER                                   │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  Data Warehouse  │  Feature Store  │  Analytics APIs  │  BI Tools     │  │
│  │   (Snowflake)    │    (Feast)      │   (GraphQL)      │  (Tableau)    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CONTROL PLANE (Self-Healing)                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  • Spark Operator (Job Lifecycle)    • KEDA (Autoscaling)            │  │
│  │  • Argo Workflows (Orchestration)    • Istio (Service Mesh)          │  │
│  │  • Prometheus (Metrics)              • Grafana (Dashboards)           │  │
│  │  • Loki (Logs)                       • Jaeger (Tracing)               │  │
│  │  • Cert-Manager (TLS)                • External Secrets Operator      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

                        STORAGE LAYER (External to K8s)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Delta Lake (S3)  │  Checkpoint Store (S3)  │  State Store (RocksDB/S3)     │
│  • Bronze tables  │  • Per-job checkpoints  │  • Streaming state            │
│  • Silver tables  │  • Recovery metadata    │  • Windowed aggregations      │
│  • Gold tables    │  • WAL logs             │  • Deduplication state        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Immutability**: Raw data is never modified; transformations create new versions
3. **Idempotency**: All operations can be safely retried
4. **Observability**: Every component emits structured logs, metrics, and traces
5. **Declarative Configuration**: Infrastructure and jobs defined as code

---

## 2. Medallion Architecture

### 2.1 Bronze Layer (Raw Ingestion)

**Purpose**: Ingest raw data from all sources with minimal transformation

**Design Decisions**:

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Data Format** | Delta Lake (Parquet + transaction log) | ACID guarantees, time travel, schema evolution |
| **Processing Mode** | Structured Streaming (continuous) + Batch (scheduled) | Real-time for Kafka/CDC, batch for S3/API |
| **Schema Strategy** | Schema-on-write with validation | Early error detection, prevents downstream corruption |
| **Deduplication** | Event-time watermarking + dropDuplicates | Exactly-once semantics for idempotent replay |
| **Checkpointing** | S3 with versioned directories | Durable, cross-zone accessible |
| **Dead Letter Queue** | Separate Delta table per source | Isolate bad records, enable manual replay |

**Example: Kafka → Bronze Stream**

```python
# Bronze ingestion from Kafka
bronze_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka-broker-0.kafka:9092,kafka-broker-1.kafka:9092")
    .option("subscribe", "events-topic")
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")  # Handle broker restarts gracefully
    .option("kafka.session.timeout.ms", "30000")
    .option("kafka.request.timeout.ms", "60000")
    .load()
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "topic", "partition", "offset", "timestamp")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("date", to_date(col("timestamp")))
    .withWatermark("timestamp", "10 minutes")  # Allow 10min late data
    .dropDuplicates(["key", "timestamp"])  # Exactly-once deduplication
)

# Write to Bronze Delta with checkpointing
query = (
    bronze_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://checkpoints/bronze/kafka-events")
    .partitionBy("date")
    .trigger(processingTime="30 seconds")  # Micro-batch interval
    .start("s3a://data-lake/bronze/events")
)
```

**Self-Healing Features**:
- **Kafka broker failure**: Automatic reconnection with exponential backoff
- **Bad records**: Schema validation → DLQ → alerting
- **Checkpoint corruption**: Fallback to last known good offset from Kafka
- **Out-of-memory**: Pod restart triggers from last checkpoint (no data loss)

### 2.2 Silver Layer (Cleaned & Enriched)

**Purpose**: Apply business logic, data quality checks, and enrichment

**Design Decisions**:

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Processing Mode** | Hybrid: Streaming for hot path, batch for backfill | Balance latency and cost |
| **Data Quality** | Great Expectations framework | Standardized validation, auto-profiling |
| **Enrichment** | Broadcast joins for small dims, shuffle for large | Optimize network transfer |
| **CDC Handling** | Delta MERGE with sequence numbers | Eventual consistency, idempotent upserts |
| **Partitioning** | Time-based (date) + business key (region) | Query optimization, partition pruning |
| **Incremental Processing** | Delta time travel + watermark tracking | Process only new/changed data |

**Example: Bronze → Silver Transformation**

```python
# Read Bronze stream
bronze_df = (
    spark.readStream
    .format("delta")
    .load("s3a://data-lake/bronze/events")
)

# Enrichment dimension (small, broadcast)
region_lookup = spark.read.format("delta").load("s3a://dimensions/regions").cache()

# Transform to Silver
silver_stream = (
    bronze_df
    .filter(col("value").isNotNull())  # Drop nulls
    .withColumn("parsed", from_json(col("value"), event_schema))
    .select("parsed.*", "ingestion_timestamp", "timestamp as event_timestamp")

    # Data quality checks
    .filter((col("user_id").isNotNull()) & (col("user_id") != ""))
    .filter(col("event_timestamp") > "2020-01-01")  # Sanity check

    # Enrichment
    .join(broadcast(region_lookup), on="region_code", how="left")

    # PII masking
    .withColumn("email_masked", regexp_replace(col("email"), "(?<=.{3}).(?=.*@)", "*"))

    # Business logic
    .withColumn("session_duration_minutes",
                (col("session_end") - col("session_start")) / 60)

    # Data type optimization
    .withColumn("amount", col("amount").cast("decimal(18,2)"))
    .withColumn("processed_timestamp", current_timestamp())
)

# Write to Silver with quality gates
query = (
    silver_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://checkpoints/silver/events")
    .option("mergeSchema", "true")  # Allow schema evolution
    .partitionBy("date", "region")
    .trigger(processingTime="60 seconds")
    .foreachBatch(lambda df, epoch_id: quality_check_and_write(df, epoch_id))
    .start("s3a://data-lake/silver/events")
)

def quality_check_and_write(batch_df, epoch_id):
    """Apply Great Expectations validation before writing"""
    ge_df = ge.from_pandas(batch_df.toPandas())

    # Define expectations
    result = ge_df.expect_column_values_to_not_be_null("user_id")
    result = ge_df.expect_column_values_to_be_between("amount", min_value=0, max_value=1000000)

    if result["success"]:
        batch_df.write.format("delta").mode("append").save("s3a://data-lake/silver/events")
    else:
        # Write failures to DLQ
        batch_df.write.format("delta").mode("append").save("s3a://data-lake/dlq/silver-quality-failures")
        raise Exception(f"Quality check failed for epoch {epoch_id}")
```

**Self-Healing Features**:
- **Schema evolution**: Automatic column addition/nullable conversion
- **Enrichment failures**: Fallback to cached dimensions, alert on staleness
- **Quality failures**: Write to DLQ, trigger alert, continue processing valid records
- **Backfill**: Time travel to reprocess specific date ranges without disrupting live stream

### 2.3 Gold Layer (Business Aggregates)

**Purpose**: Create curated, analytics-ready datasets

**Design Decisions**:

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Processing Mode** | Scheduled batch jobs (Argo Workflows) | Deterministic, testable, cost-effective |
| **Aggregation Strategy** | Pre-compute common metrics | Trade storage for query speed |
| **Time Windows** | Multiple granularities (hourly, daily, weekly) | Support diverse analytics use cases |
| **SCD Handling** | Type 2 slowly changing dimensions | Historical accuracy for point-in-time queries |
| **Feature Store Integration** | Feast materialization | Low-latency serving for ML models |
| **Data Compaction** | Z-ordering + OPTIMIZE | Query performance, storage efficiency |

**Example: Silver → Gold Aggregation**

```python
# Scheduled job (runs every hour via Argo CronWorkflow)
from pyspark.sql.window import Window

# Read Silver table (incremental)
silver_df = (
    spark.read.format("delta")
    .option("versionAsOf", get_last_processed_version())  # Incremental processing
    .load("s3a://data-lake/silver/events")
    .filter(col("date") > get_last_processed_date())
)

# Gold aggregation: Daily user metrics
gold_daily_metrics = (
    silver_df
    .groupBy("date", "user_id", "region")
    .agg(
        count("*").alias("event_count"),
        sum("amount").alias("total_amount"),
        avg("session_duration_minutes").alias("avg_session_duration"),
        countDistinct("session_id").alias("unique_sessions"),
        first("email_masked").alias("email"),  # Dimension attributes
        first("region_name").alias("region_name")
    )
    .withColumn("amount_percentile_rank",
                percent_rank().over(Window.partitionBy("date").orderBy("total_amount")))
    .withColumn("processed_timestamp", current_timestamp())
    .withColumn("data_version", lit(DATA_VERSION))  # For reproducibility
)

# Write with MERGE for idempotency
def merge_to_gold(df, table_path):
    """Upsert to Gold table using Delta MERGE"""
    delta_table = DeltaTable.forPath(spark, table_path)

    delta_table.alias("target").merge(
        df.alias("source"),
        "target.date = source.date AND target.user_id = source.user_id"
    ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

    # Optimize table
    delta_table.optimize().executeZOrderBy("user_id", "date")

merge_to_gold(gold_daily_metrics, "s3a://data-lake/gold/daily_user_metrics")

# Materialize to Feature Store
gold_daily_metrics.write.format("feast").mode("append").save()
```

**Self-Healing Features**:
- **Job failure**: Argo retry with exponential backoff (3 attempts)
- **Data drift**: Automated validation against expected distributions
- **Incremental reprocessing**: Time travel + version tracking enables targeted fixes
- **Zombie jobs**: Kubernetes liveness probes terminate hung processes

---

## 3. Recovery Flow Design

### 3.1 Checkpoint Directory Structure

```
s3://pipeline-checkpoints/
├── bronze/
│   ├── kafka-events/
│   │   ├── commits/
│   │   │   ├── 0                          # Batch 0 metadata
│   │   │   ├── 1
│   │   │   └── 2
│   │   ├── offsets/
│   │   │   ├── 0                          # Kafka offsets for batch 0
│   │   │   ├── 1
│   │   │   └── 2
│   │   ├── metadata                        # Query metadata
│   │   └── sources/
│   │       └── 0/
│   │           └── 0                       # Source metadata (Kafka topics)
│   │
│   └── s3-batch-ingestion/
│       ├── commits/
│       ├── metadata
│       └── state/
│           └── 0/                          # State store for deduplication
│               └── 0/
│                   └── 1.delta             # RocksDB snapshot
│
├── silver/
│   ├── events-cleansing/
│   │   ├── commits/
│   │   ├── offsets/
│   │   ├── metadata
│   │   └── state/                          # Stateful transformations
│   │       └── 0/
│   │           ├── 0/
│   │           │   └── 1.delta             # Windowed aggregation state
│   │           └── 1/
│   │               └── 1.delta
│   │
│   └── enrichment/
│       └── [similar structure]
│
└── gold/
    └── [batch jobs use Delta transaction log, not checkpoints]
```

### 3.2 State Store Configuration

**Decision Matrix**:

| Scenario | State Backend | Rationale |
|----------|--------------|-----------|
| **Streaming with windows < 1 hour** | RocksDB (local SSD) + S3 snapshots | Low-latency state access, durable backups |
| **Streaming with windows > 1 hour** | RocksDB with frequent S3 snapshots | Balance memory and durability |
| **Stateless transformations** | No state store needed | Minimize overhead |
| **Join with small dimension** | Broadcast join (in-memory) | Avoid shuffle, reduce state size |
| **Deduplication** | RocksDB with compaction | Efficient key lookups |

**RocksDB Configuration (Production)**:

```python
spark_conf = {
    # State store backend
    "spark.sql.streaming.stateStore.providerClass": "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",

    # RocksDB tuning
    "spark.sql.streaming.stateStore.rocksdb.compactOnCommit": "true",
    "spark.sql.streaming.stateStore.rocksdb.blockSizeKB": "32",  # 32KB blocks
    "spark.sql.streaming.stateStore.rocksdb.blockCacheSizeMB": "512",  # 512MB cache per executor
    "spark.sql.streaming.stateStore.rocksdb.maxOpenFiles": "1000",

    # Checkpointing
    "spark.sql.streaming.checkpointLocation": "s3a://checkpoints/",
    "spark.sql.streaming.minBatchesToRetain": "100",  # Keep last 100 batches

    # State management
    "spark.sql.streaming.stateStore.maintenanceInterval": "60s",  # Cleanup interval
    "spark.sql.streaming.statefulOperator.checkCorrectness.enabled": "true"  # Validate state
}
```

### 3.3 Exactly-Once Semantics Guarantees

**End-to-End Flow**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EXACTLY-ONCE GUARANTEE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SOURCE (Kafka)                                                      │
│    ↓ [Consumer with group.id, enable.auto.commit=false]             │
│    • Read batch of records                                           │
│    • Track offsets in checkpoint (not committed to Kafka yet)        │
│                                                                      │
│  PROCESSING (Spark)                                                  │
│    ↓ [Idempotent transformations]                                    │
│    • Transform data (deterministic operations)                       │
│    • Write to Delta with transaction ID                              │
│    • Delta ensures atomic write (all or nothing)                     │
│                                                                      │
│  CHECKPOINT COMMIT (Atomic)                                          │
│    ↓ [Two-phase commit coordination]                                 │
│    1. Write data to Delta → Delta transaction log updated            │
│    2. Write offsets to checkpoint directory → S3 atomic put          │
│    3. Only if BOTH succeed: batch considered complete                │
│                                                                      │
│  FAILURE SCENARIOS:                                                  │
│    • Crash before checkpoint commit → Replay from last checkpoint    │
│    • Crash after data write, before checkpoint → Replay (idempotent) │
│    • Crash after checkpoint → Continue from next batch               │
│                                                                      │
│  RESULT: Each record processed exactly once (no duplicates/losses)   │
└─────────────────────────────────────────────────────────────────────┘
```

**Code Pattern**:

```python
# Exactly-once configuration
kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKERS)
    .option("subscribe", "events")
    .option("kafka.group.id", "spark-consumer-group-v1")
    .option("enable.auto.commit", "false")  # Manual offset management
    .option("kafka.isolation.level", "read_committed")  # Only read committed Kafka messages
    .load()
)

# Write with exactly-once semantics
query = (
    kafka_stream
    .writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://checkpoints/bronze/kafka-events")
    .option("queryName", "kafka-to-bronze-v1")  # Stable query name
    .trigger(processingTime="30 seconds")
    .start("s3a://data-lake/bronze/events")
)
```

### 3.4 Recovery Scenarios

| Failure Type | Detection | Recovery Action | Expected RTO |
|--------------|-----------|-----------------|--------------|
| **Pod crash** | Kubernetes liveness probe | Restart pod → Resume from checkpoint | < 2 min |
| **Executor OOM** | Spark driver logs | Increase memory, restart → Resume | < 5 min |
| **Checkpoint corruption** | Read failure on startup | Fallback to previous checkpoint version | < 10 min |
| **S3 throttling** | 503 errors | Exponential backoff + retry | < 1 min |
| **Kafka broker down** | Connection timeout | Reconnect to other brokers | < 30 sec |
| **Schema mismatch** | Parse exception | Route to DLQ, alert, continue | < 1 min |
| **Network partition** | Timeout errors | Retry with backoff, re-establish connection | < 2 min |
| **State store corruption** | Checksum mismatch | Rebuild state from Delta table + WAL | < 30 min |

**Automated Recovery Workflow**:

```yaml
# Kubernetes Job with restart policy
apiVersion: batch/v1
kind: Job
metadata:
  name: bronze-kafka-ingestion
spec:
  backoffLimit: 3  # Retry 3 times
  activeDeadlineSeconds: 3600  # Fail after 1 hour
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: spark-driver
        image: spark:3.5.0
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /metrics/json
            port: 4040
          initialDelaySeconds: 300
          periodSeconds: 60
          failureThreshold: 3
```

---

## 4. Backpressure Handling

### 4.1 Rate Limiting Configuration

**Problem**: Overwhelming downstream systems during spikes

**Solution**: Adaptive rate limiting at each layer

```python
# Bronze layer: Rate limit Kafka consumption
bronze_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKERS)
    .option("subscribe", "events")
    .option("maxOffsetsPerTrigger", "10000")  # Max 10K records per micro-batch
    .option("minPartitions", "10")  # Distribute across 10 partitions
    .load()
)

# Silver layer: Adaptive batch sizing
silver_query = (
    silver_stream.writeStream
    .format("delta")
    .trigger(processingTime="60 seconds")  # Fixed interval
    .option("spark.sql.streaming.fileSource.maxFilesPerTrigger", "100")  # Limit files read
    .start()
)

# Gold layer: Throttle with Argo Workflows
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata:
  name: gold-aggregation
spec:
  schedule: "0 * * * *"  # Every hour
  concurrencyPolicy: Forbid  # Prevent overlapping runs
  suspend: false
  workflowSpec:
    podGC:
      strategy: OnPodSuccess
    ttlStrategy:
      secondsAfterCompletion: 86400  # Clean up after 24h
    templates:
    - name: aggregate
      container:
        image: spark:3.5.0
        resources:
          limits:
            memory: "16Gi"
            cpu: "8"
```

### 4.2 Adaptive Batch Sizing

**Dynamic Adjustment Based on Lag**:

```python
from pyspark.sql.streaming import StreamingQueryListener

class BackpressureListener(StreamingQueryListener):
    def onQueryProgress(self, event):
        progress = event.progress
        input_rows = progress.numInputRows
        processing_time_ms = progress.durationMs["triggerExecution"]

        # Calculate processing rate (rows/sec)
        processing_rate = (input_rows / processing_time_ms) * 1000 if processing_time_ms > 0 else 0

        # Adjust maxOffsetsPerTrigger dynamically
        current_lag_seconds = self.calculate_lag(progress)

        if current_lag_seconds > 300:  # Lag > 5 minutes
            new_rate = int(processing_rate * 1.5)  # Increase by 50%
            self.update_rate_limit(new_rate)
        elif current_lag_seconds < 60:  # Lag < 1 minute
            new_rate = int(processing_rate * 0.8)  # Decrease by 20%
            self.update_rate_limit(new_rate)

        # Emit metrics
        prometheus_client.Gauge('spark_processing_rate').set(processing_rate)
        prometheus_client.Gauge('spark_lag_seconds').set(current_lag_seconds)

# Register listener
spark.streams.addListener(BackpressureListener())
```

### 4.3 Queue Depth Monitoring

**Kafka Lag Monitoring**:

```yaml
# Prometheus ServiceMonitor for Kafka lag
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kafka-lag-exporter
spec:
  selector:
    matchLabels:
      app: kafka-lag-exporter
  endpoints:
  - port: metrics
    interval: 30s

# Alert on high lag
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: spark-backpressure-alerts
spec:
  groups:
  - name: streaming
    interval: 30s
    rules:
    - alert: KafkaLagHigh
      expr: kafka_consumergroup_lag{group="spark-consumer-group-v1"} > 100000
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Kafka consumer lag is high (> 100K messages)"
        description: "Consumer group {{ $labels.group }} has lag of {{ $value }} messages"

    - alert: SparkProcessingSlowdown
      expr: rate(spark_streaming_processed_rows_total[5m]) < 100
      for: 10m
      labels:
        severity: critical
      annotations:
        summary: "Spark processing rate dropped below 100 rows/sec"
```

**Self-Healing Actions**:

```python
# In Spark application
def handle_backpressure(current_lag_seconds):
    """Automatic scaling based on lag"""
    if current_lag_seconds > 600:  # 10 minutes
        # Request horizontal scale-up via Kubernetes API
        k8s_client.scale_deployment(
            name="bronze-kafka-ingestion",
            namespace="data-pipelines",
            replicas=current_replicas + 2
        )
        logger.warning(f"Scaled up to {current_replicas + 2} replicas due to lag")

    elif current_lag_seconds < 120 and current_replicas > 2:  # 2 minutes, min 2 replicas
        # Scale down to save costs
        k8s_client.scale_deployment(
            name="bronze-kafka-ingestion",
            namespace="data-pipelines",
            replicas=current_replicas - 1
        )
        logger.info(f"Scaled down to {current_replicas - 1} replicas")
```

---

## 5. High Availability Design

### 5.1 Multi-Replica Deployments

**Deployment Strategy**:

| Component | Replicas | Anti-Affinity | Rationale |
|-----------|----------|--------------|-----------|
| **Bronze Kafka Stream** | 2 | Preferred zone | Active-active, partition consumption |
| **Bronze S3 Batch** | 2 | Preferred zone | Primary-standby, file-based coordination |
| **Silver Cleansing** | 3 | Required zone | Active-active, high throughput |
| **Silver Enrichment** | 2 | Preferred zone | Active-active, moderate load |
| **Gold Aggregation** | 1 (batch) | N/A | Scheduled, single-run |
| **Kafka Brokers** | 3 | Required zone | Consensus, fault tolerance |
| **Spark Operator** | 2 | Required node | Leader election (Kubernetes) |

**Example Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bronze-kafka-ingestion
  namespace: data-pipelines
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
  selector:
    matchLabels:
      app: bronze-kafka-ingestion
  template:
    metadata:
      labels:
        app: bronze-kafka-ingestion
    spec:
      # Anti-affinity: Spread across zones
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - bronze-kafka-ingestion
              topologyKey: topology.kubernetes.io/zone

      # Service account for Spark
      serviceAccountName: spark-driver

      containers:
      - name: spark-driver
        image: spark:3.5.0
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"

        # Health checks
        livenessProbe:
          httpGet:
            path: /metrics/json
            port: 4040
          initialDelaySeconds: 300
          periodSeconds: 60
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /metrics/json
            port: 4040
          initialDelaySeconds: 180
          periodSeconds: 30

        env:
        - name: SPARK_DRIVER_MEMORY
          value: "6g"
        - name: SPARK_EXECUTOR_MEMORY
          value: "4g"
        - name: SPARK_EXECUTOR_INSTANCES
          value: "10"
```

### 5.2 Leader Election for Singleton Components

**Problem**: Some components must run as singletons (e.g., Spark Operator, schema registry sync)

**Solution**: Kubernetes-native leader election

```python
# Python leader election using Kubernetes API
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time

def acquire_leadership(lease_name, namespace, identity):
    """Acquire leadership using Kubernetes Lease object"""
    config.load_incluster_config()
    coordination_v1 = client.CoordinationV1Api()

    while True:
        try:
            # Try to get existing lease
            lease = coordination_v1.read_namespaced_lease(lease_name, namespace)

            if lease.spec.holder_identity == identity:
                # We are the leader, renew lease
                lease.spec.renew_time = datetime.datetime.utcnow()
                coordination_v1.replace_namespaced_lease(lease_name, namespace, lease)
                return True

            elif (datetime.datetime.utcnow() - lease.spec.renew_time).seconds > 30:
                # Current leader is dead, acquire leadership
                lease.spec.holder_identity = identity
                lease.spec.acquire_time = datetime.datetime.utcnow()
                lease.spec.renew_time = datetime.datetime.utcnow()
                coordination_v1.replace_namespaced_lease(lease_name, namespace, lease)
                return True

            else:
                # Another leader is active, wait
                time.sleep(10)

        except ApiException as e:
            if e.status == 404:
                # Create new lease
                lease = client.V1Lease(
                    metadata=client.V1ObjectMeta(name=lease_name, namespace=namespace),
                    spec=client.V1LeaseSpec(
                        holder_identity=identity,
                        lease_duration_seconds=30,
                        acquire_time=datetime.datetime.utcnow(),
                        renew_time=datetime.datetime.utcnow()
                    )
                )
                coordination_v1.create_namespaced_lease(namespace, lease)
                return True

# In main application
if __name__ == "__main__":
    pod_name = os.getenv("HOSTNAME")  # Kubernetes pod name

    if acquire_leadership("spark-operator-leader", "data-pipelines", pod_name):
        logger.info(f"Pod {pod_name} acquired leadership")
        run_operator()  # Start actual work
    else:
        logger.info(f"Pod {pod_name} is standby")
        standby_mode()  # Wait for leadership
```

### 5.3 Cross-Zone Distribution

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────┐│
│  │     ZONE A         │  │     ZONE B         │  │     ZONE C     ││
│  ├────────────────────┤  ├────────────────────┤  ├────────────────┤│
│  │ Kafka Broker 0     │  │ Kafka Broker 1     │  │ Kafka Broker 2 ││
│  │ (Leader for P0,P3) │  │ (Leader for P1,P4) │  │ (Leader for P2)││
│  │                    │  │                    │  │                ││
│  │ Spark Driver 1     │  │ Spark Driver 2     │  │                ││
│  │ (Executors: E1-E4) │  │ (Executors: E5-E8) │  │ (Executors:E9) ││
│  │                    │  │                    │  │                ││
│  │ Silver Job A       │  │ Silver Job B       │  │ Gold Job       ││
│  └────────────────────┘  └────────────────────┘  └────────────────┘│
│                                                                      │
│  Network: Low-latency cross-zone communication (< 5ms)              │
│  Storage: S3 (zone-redundant, accessible from all zones)            │
└─────────────────────────────────────────────────────────────────────┘

FAILURE SCENARIO: Zone A fails
├─ Kafka: Partition leaders re-elected in Zone B/C (< 10 sec)
├─- Spark: Executors in Zone A lost, re-created in Zone B/C (< 2 min)
└─- Jobs: Restart from checkpoint, resume processing (< 3 min)
```

**Kubernetes Configuration**:

```yaml
# Node affinity to prefer zone distribution
apiVersion: v1
kind: Pod
metadata:
  name: spark-executor-1
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values:
            - us-west-2a
            - us-west-2b
            - us-west-2c

  # Tolerate zone failures
  tolerations:
  - key: "node.kubernetes.io/unreachable"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 30  # Wait 30s before evicting
```

---

## 6. Data Flow Diagrams

### 6.1 Real-Time Streaming Path (Bronze → Silver)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME STREAMING PATH (< 1 min latency)              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  KAFKA CLUSTER (3 brokers, RF=3)                                             │
│    Topic: events (10 partitions)                                             │
│    ↓                                                                          │
│    • Message: {user_id, event_type, timestamp, payload}                      │
│    • Retention: 7 days                                                        │
│    • Throughput: 10K msgs/sec                                                 │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ BRONZE SPARK STREAMING JOB (Replicas: 2)                        │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Read from Kafka                                              │        │
│  │    • Subscribe to 'events' topic                                │        │
│  │    • maxOffsetsPerTrigger: 10K                                  │        │
│  │    • Trigger: 30 seconds                                        │        │
│  │                                                                  │        │
│  │ 2. Schema Validation                                            │        │
│  │    • Parse JSON payload                                         │        │
│  │    • Validate against schema registry                           │        │
│  │    • Invalid → DLQ (s3://dlq/bronze-schema-failures)            │        │
│  │                                                                  │        │
│  │ 3. Deduplication                                                │        │
│  │    • Watermark: 10 minutes                                      │        │
│  │    • dropDuplicates(user_id, timestamp)                         │        │
│  │    • State store: RocksDB (local + S3 snapshots)                │        │
│  │                                                                  │        │
│  │ 4. Write to Delta Lake                                          │        │
│  │    • Format: Parquet + transaction log                          │        │
│  │    • Partition: by date                                         │        │
│  │    • Checkpoint: s3://checkpoints/bronze/kafka-events           │        │
│  │    • Output: s3://data-lake/bronze/events                       │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                              ↓                                                │
│  DELTA LAKE: bronze.events                                                   │
│    • Schema: [user_id, event_type, timestamp, payload, date]                 │
│    • Size: ~500GB (30 days retention)                                        │
│    • Partitions: 30 (one per day)                                            │
│                              ↓                                                │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ SILVER SPARK STREAMING JOB (Replicas: 3)                        │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Read from Bronze Delta                                       │        │
│  │    • readStream.format("delta")                                 │        │
│  │    • Trigger: 60 seconds                                        │        │
│  │                                                                  │        │
│  │ 2. Data Cleansing                                               │        │
│  │    • Remove nulls in critical fields                            │        │
│  │    • Trim whitespace                                            │        │
│  │    • Standardize formats (dates, phone numbers)                 │        │
│  │                                                                  │        │
│  │ 3. Enrichment                                                   │        │
│  │    • Broadcast join with dimension tables:                      │        │
│  │      - users (cached, 10M rows)                                 │        │
│  │      - regions (cached, 1K rows)                                │        │
│  │    • Add derived columns (session_duration, amount_usd)         │        │
│  │                                                                  │        │
│  │ 4. PII Masking                                                  │        │
│  │    • Email: show first 3 chars + ***@domain.com                 │        │
│  │    • Phone: show last 4 digits                                  │        │
│  │                                                                  │        │
│  │ 5. Quality Checks (Great Expectations)                          │        │
│  │    • Expect user_id not null                                    │        │
│  │    • Expect amount >= 0                                         │        │
│  │    • Expect timestamp within last 7 days                        │        │
│  │    • Failed rows → DLQ                                          │        │
│  │                                                                  │        │
│  │ 6. Write to Delta Lake                                          │        │
│  │    • Partition: by date, region                                 │        │
│  │    • Checkpoint: s3://checkpoints/silver/events                 │        │
│  │    • Output: s3://data-lake/silver/events                       │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                              ↓                                                │
│  DELTA LAKE: silver.events                                                   │
│    • Schema: [user_id, event_type, timestamp, amount_usd, region, ...]       │
│    • Size: ~800GB (enriched + indexed)                                       │
│    • Partitions: 30 dates × 5 regions = 150 partitions                       │
│    • Z-Ordered by: user_id                                                   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

LATENCY BREAKDOWN:
├─ Kafka → Bronze: 30 sec (micro-batch interval)
├─ Bronze → Delta write: 5 sec (I/O)
├─ Delta → Silver read: 10 sec (discovery)
├─ Silver processing: 20 sec (transform + quality)
├─ Silver → Delta write: 15 sec (I/O)
└─ TOTAL: ~80 seconds (end-to-end)

THROUGHPUT:
├─ Kafka: 10K msgs/sec = 600K msgs/min
├─ Bronze: 20K rows/micro-batch = 40K rows/min
└─ Silver: 35K rows/min (after filtering ~12% for quality failures)
```

### 6.2 Batch Processing Path (Bronze → Gold)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BATCH PROCESSING PATH (hourly schedule)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ARGO CRON WORKFLOW (Schedule: "0 * * * *")                                  │
│    Triggered: Every hour at :00                                              │
│    ↓                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ GOLD AGGREGATION JOB (Single replica)                           │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Read Silver Delta (Incremental)                              │        │
│  │    • Read only last hour's data (date partition filter)         │        │
│  │    • Delta time travel: versionAsOf(previous_version)           │        │
│  │    • Input: ~2M rows (1 hour)                                   │        │
│  │                                                                  │        │
│  │ 2. Aggregations                                                 │        │
│  │    a) Daily user metrics:                                       │        │
│  │       • GROUP BY date, user_id                                  │        │
│  │       • AGG: count, sum(amount), avg(session_duration)          │        │
│  │                                                                  │        │
│  │    b) Regional rollups:                                         │        │
│  │       • GROUP BY date, region                                   │        │
│  │       • AGG: count, sum(amount), unique users                   │        │
│  │                                                                  │        │
│  │    c) ML features:                                              │        │
│  │       • User behavior vectors (7-day, 30-day windows)           │        │
│  │       • Churn probability scores                                │        │
│  │       • Lifetime value predictions                              │        │
│  │                                                                  │        │
│  │ 3. Slowly Changing Dimensions (SCD Type 2)                      │        │
│  │    • Track user attribute changes (e.g., region move)           │        │
│  │    • Maintain history with effective_from/effective_to          │        │
│  │                                                                  │        │
│  │ 4. Data Quality Validation                                      │        │
│  │    • Check for data drift (distribution changes)                │        │
│  │    • Validate row counts vs expected                            │        │
│  │    • Alert on anomalies (> 2 std devs)                          │        │
│  │                                                                  │        │
│  │ 5. Write to Gold Delta (MERGE)                                  │        │
│  │    • Upsert into target tables (idempotent)                     │        │
│  │    • MERGE ON (date, user_id/region)                            │        │
│  │    • WHEN MATCHED: UPDATE                                       │        │
│  │    • WHEN NOT MATCHED: INSERT                                   │        │
│  │                                                                  │        │
│  │ 6. Table Optimization                                           │        │
│  │    • OPTIMIZE table (compact small files)                       │        │
│  │    • Z-ORDER BY (user_id, date) for query performance           │        │
│  │    • VACUUM (delete files > 30 days old)                        │        │
│  │                                                                  │        │
│  │ 7. Materialize to Feature Store                                 │        │
│  │    • Write ML features to Feast (Redis online store)            │        │
│  │    • Register in feature registry                               │        │
│  │    • Enable low-latency serving (< 10ms p99)                    │        │
│  └──────────────────────────┬──────────────────────────────────────┘        │
│                              ↓                                                │
│  DELTA LAKE: gold.daily_user_metrics                                         │
│    • Schema: [date, user_id, event_count, total_amount, ...]                 │
│    • Size: ~50GB (90 days)                                                   │
│    • Partitions: 90 (one per day)                                            │
│    • Query SLA: < 5 sec for typical analytics queries                        │
│                              ↓                                                │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ SERVING LAYER                                                   │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │                                                                  │        │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐│        │
│  │  │ SNOWFLAKE        │  │ FEAST             │  │ TABLEAU       ││        │
│  │  │ (Data Warehouse) │  │ (Feature Store)   │  │ (BI Tool)     ││        │
│  │  ├──────────────────┤  ├──────────────────┤  ├───────────────┤│        │
│  │  │ • Incremental    │  │ • Online store   │  │ • Dashboards  ││        │
│  │  │   load from Gold │  │   (Redis)        │  │ • Reports     ││        │
│  │  │ • COPY command   │  │ • Offline store  │  │ • Ad-hoc SQL  ││        │
│  │  │   (Delta → SF)   │  │   (S3)           │  │ • Refresh:    ││        │
│  │  │ • Refresh:       │  │ • Serving:       │  │   hourly      ││        │
│  │  │   hourly         │  │   < 10ms p99     │  │               ││        │
│  │  └──────────────────┘  └──────────────────┘  └───────────────┘│        │
│  │                                                                  │        │
│  └──────────────────────────────────────────────────────────────────┘        │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

PROCESSING TIME:
├─ Read Silver (1 hour data): 2 min
├─ Aggregations: 5 min
├─ MERGE to Gold: 3 min
├─ OPTIMIZE + Z-ORDER: 8 min
├─ Feast materialization: 2 min
└─ TOTAL: ~20 minutes per run

RESOURCE USAGE:
├─ Spark driver: 4 CPU, 8 GB RAM
├─ Spark executors: 20 × (4 CPU, 16 GB RAM) = 80 CPU, 320 GB RAM
├─ Peak memory: 400 GB (during aggregations)
└─ Cost: ~$15/run (on-demand pricing)
```

### 6.3 Self-Healing Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SELF-HEALING RECOVERY FLOW                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ FAILURE DETECTED                                                │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ Type: Pod crash (OOMKilled)                                     │        │
│  │ Component: Silver enrichment job                                │        │
│  │ Timestamp: 2025-12-04T14:23:45Z                                 │        │
│  │ Last checkpoint: batch 1245                                     │        │
│  └────────────────────────┬────────────────────────────────────────┘        │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ KUBERNETES REACTION (< 10 seconds)                              │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Liveness probe fails (3 consecutive failures)                │        │
│  │ 2. Pod status: CrashLoopBackOff → Terminating                   │        │
│  │ 3. ReplicaSet creates new pod in different zone                 │        │
│  │ 4. New pod: Pending → ContainerCreating → Running               │        │
│  │ 5. Init containers: Download checkpoint metadata from S3        │        │
│  └────────────────────────┬────────────────────────────────────────┘        │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ SPARK DRIVER RESTART (< 60 seconds)                             │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Read checkpoint directory:                                   │        │
│  │    s3://checkpoints/silver/enrichment/                          │        │
│  │                                                                  │        │
│  │ 2. Recover metadata:                                            │        │
│  │    • Last committed batch: 1245                                 │        │
│  │    • Source offsets: {partition_0: 98234, partition_1: 98156}   │        │
│  │    • State store version: 1245                                  │        │
│  │                                                                  │        │
│  │ 3. Validate checkpoint integrity:                               │        │
│  │    • Checksum validation: PASS                                  │        │
│  │    • Transaction log consistency: PASS                          │        │
│  │                                                                  │        │
│  │ 4. Restore state store:                                         │        │
│  │    • Download RocksDB snapshot from S3                          │        │
│  │    • Load into local SSD (NVMe)                                 │        │
│  │    • State size: 2.3 GB                                         │        │
│  │                                                                  │        │
│  │ 5. Resume streaming query:                                      │        │
│  │    • Start from batch 1246 (next after last commit)             │        │
│  │    • Reprocess in-flight micro-batch (idempotent)               │        │
│  │    • No data loss, no duplicates                                │        │
│  └────────────────────────┬────────────────────────────────────────┘        │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ EXECUTOR REALLOCATION (< 90 seconds)                            │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Request executors from Kubernetes:                           │        │
│  │    • spark.dynamicAllocation.enabled=true                       │        │
│  │    • Initial executors: 10                                      │        │
│  │    • Max executors: 50                                          │        │
│  │                                                                  │        │
│  │ 2. Kubernetes creates executor pods:                            │        │
│  │    • 10 pods scheduled across 3 zones                           │        │
│  │    • Resource allocation: 4 CPU, 16 GB RAM each                 │        │
│  │                                                                  │        │
│  │ 3. Executors register with driver:                              │        │
│  │    • Heartbeat interval: 10 seconds                             │        │
│  │    • Timeout: 120 seconds                                       │        │
│  │                                                                  │        │
│  │ 4. Resume task execution:                                       │        │
│  │    • Recompute lost RDD partitions (if any)                     │        │
│  │    • Continue processing from checkpoint                        │        │
│  └────────────────────────┬────────────────────────────────────────┘        │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ POST-RECOVERY VALIDATION (< 5 minutes)                          │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Verify data continuity:                                      │        │
│  │    • Check row counts: expected = 98234 - 98156 = 78 rows       │        │
│  │    • Actual rows written: 78 ✓                                  │        │
│  │                                                                  │        │
│  │ 2. Validate processing lag:                                     │        │
│  │    • Current lag: 45 seconds (acceptable)                       │        │
│  │    • Lag spike during recovery: 2 minutes (expected)            │        │
│  │                                                                  │        │
│  │ 3. Check downstream impact:                                     │        │
│  │    • Gold jobs: No impact (hourly schedule)                     │        │
│  │    • Serving layer: No stale data                               │        │
│  │                                                                  │        │
│  │ 4. Send recovery notification:                                  │        │
│  │    • Slack alert: "Silver enrichment job recovered"             │        │
│  │    • PagerDuty: Auto-resolve incident                           │        │
│  │    • Grafana: Annotate recovery event on dashboard              │        │
│  └────────────────────────┬────────────────────────────────────────┘        │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │ ROOT CAUSE ANALYSIS (Automated)                                 │        │
│  ├─────────────────────────────────────────────────────────────────┤        │
│  │ 1. Collect diagnostics:                                         │        │
│  │    • Pod logs (last 1000 lines)                                 │        │
│  │    • Metrics: Memory usage spiked to 15 GB (limit: 16 GB)       │        │
│  │    • Spark UI: Large shuffle (10 GB)                            │        │
│  │                                                                  │        │
│  │ 2. Identify cause:                                              │        │
│  │    • OOMKilled due to large broadcast join                      │        │
│  │    • Recommendation: Increase executor memory to 24 GB          │        │
│  │                                                                  │        │
│  │ 3. Auto-remediation:                                            │        │
│  │    • Update Deployment: memory limit 16 GB → 24 GB              │        │
│  │    • GitOps commit: Pull request auto-created                   │        │
│  │    • Apply after approval                                       │        │
│  │                                                                  │        │
│  │ 4. Prevent recurrence:                                          │        │
│  │    • Add Prometheus alert: memory > 80% for 5 min               │        │
│  │    • Update runbook with mitigation steps                       │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

RECOVERY METRICS:
├─ Detection time: 10 seconds (liveness probe)
├─ Pod restart: 45 seconds (image pull + init)
├─ Checkpoint recovery: 30 seconds (S3 read + validation)
├─ State restore: 20 seconds (RocksDB load)
├─ Executor allocation: 60 seconds (pod scheduling)
├─ Processing resume: 15 seconds (first micro-batch)
└─ TOTAL RTO: ~3 minutes (from failure to full recovery)

DATA INTEGRITY:
├─ Records lost: 0 (exactly-once semantics)
├─ Records duplicated: 0 (checkpoint-based deduplication)
├─ Downstream impact: None (recovery transparent to consumers)
└─ SLA compliance: 99.95% uptime (< 5 min downtime per month)
```

---

## 7. Configuration Patterns

### 7.1 Spark Configuration (Production-Ready)

```python
# spark_config.py
"""Production Spark configuration for self-healing pipelines"""

def get_bronze_streaming_config():
    """Bronze layer: High throughput, fault-tolerant"""
    return {
        # Application
        "spark.app.name": "bronze-kafka-ingestion-v2",
        "spark.submit.deployMode": "cluster",

        # Driver
        "spark.driver.memory": "6g",
        "spark.driver.cores": "2",
        "spark.driver.memoryOverhead": "2g",

        # Executors
        "spark.executor.memory": "4g",
        "spark.executor.cores": "4",
        "spark.executor.memoryOverhead": "1g",
        "spark.executor.instances": "10",  # Initial

        # Dynamic allocation
        "spark.dynamicAllocation.enabled": "true",
        "spark.dynamicAllocation.minExecutors": "5",
        "spark.dynamicAllocation.maxExecutors": "50",
        "spark.dynamicAllocation.initialExecutors": "10",
        "spark.dynamicAllocation.executorIdleTimeout": "300s",
        "spark.dynamicAllocation.schedulerBacklogTimeout": "5s",

        # Shuffle
        "spark.shuffle.service.enabled": "true",
        "spark.shuffle.service.port": "7337",
        "spark.shuffle.compress": "true",
        "spark.shuffle.spill.compress": "true",

        # Serialization
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.kryoserializer.buffer.max": "512m",

        # Checkpointing
        "spark.sql.streaming.checkpointLocation": "s3a://checkpoints/bronze/kafka-events",
        "spark.sql.streaming.minBatchesToRetain": "100",

        # State store (RocksDB)
        "spark.sql.streaming.stateStore.providerClass":
            "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",
        "spark.sql.streaming.stateStore.rocksdb.compactOnCommit": "true",
        "spark.sql.streaming.stateStore.rocksdb.blockSizeKB": "32",
        "spark.sql.streaming.stateStore.rocksdb.blockCacheSizeMB": "512",

        # Fault tolerance
        "spark.task.maxFailures": "4",
        "spark.stage.maxConsecutiveAttempts": "4",
        "spark.blacklist.enabled": "true",
        "spark.blacklist.timeout": "1h",

        # Networking
        "spark.network.timeout": "600s",
        "spark.executor.heartbeatInterval": "30s",
        "spark.rpc.askTimeout": "600s",

        # S3 (assume IAM role for auth)
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.fast.upload": "true",
        "spark.hadoop.fs.s3a.multipart.size": "104857600",  # 100MB
        "spark.hadoop.fs.s3a.fast.upload.buffer": "bytebuffer",
        "spark.hadoop.fs.s3a.connection.maximum": "200",
        "spark.hadoop.fs.s3a.threads.max": "64",

        # Delta Lake
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.databricks.delta.retentionDurationCheck.enabled": "false",

        # Monitoring
        "spark.metrics.conf.*.sink.prometheus.class":
            "org.apache.spark.metrics.sink.PrometheusServlet",
        "spark.metrics.conf.*.sink.prometheus.path": "/metrics",
        "spark.ui.prometheus.enabled": "true",

        # Logging
        "spark.eventLog.enabled": "true",
        "spark.eventLog.dir": "s3a://spark-logs/bronze-kafka",
        "spark.history.fs.logDirectory": "s3a://spark-logs/",
    }

def get_silver_streaming_config():
    """Silver layer: Stateful transformations, enrichment"""
    base_config = get_bronze_streaming_config()
    base_config.update({
        "spark.app.name": "silver-enrichment-v2",

        # Higher memory for joins
        "spark.executor.memory": "8g",
        "spark.executor.memoryOverhead": "2g",
        "spark.driver.memory": "8g",

        # Broadcast join threshold
        "spark.sql.autoBroadcastJoinThreshold": "100MB",

        # Adaptive query execution
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",

        # Checkpointing
        "spark.sql.streaming.checkpointLocation": "s3a://checkpoints/silver/enrichment",
    })
    return base_config

def get_gold_batch_config():
    """Gold layer: Large aggregations, scheduled batch"""
    return {
        "spark.app.name": "gold-aggregation-v2",

        # Larger resources for complex aggregations
        "spark.driver.memory": "16g",
        "spark.driver.cores": "4",
        "spark.executor.memory": "16g",
        "spark.executor.cores": "8",
        "spark.executor.instances": "20",

        # Disable dynamic allocation (batch job)
        "spark.dynamicAllocation.enabled": "false",

        # Aggressive caching
        "spark.memory.fraction": "0.8",
        "spark.memory.storageFraction": "0.3",

        # Shuffle optimization
        "spark.sql.shuffle.partitions": "200",
        "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB

        # Adaptive query execution
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.minPartitionSize": "1MB",

        # Delta Lake optimization
        "spark.databricks.delta.optimizeWrite.enabled": "true",
        "spark.databricks.delta.autoCompact.enabled": "true",

        # S3 (same as streaming)
        **{k: v for k, v in get_bronze_streaming_config().items() if "s3a" in k},

        # Monitoring
        "spark.metrics.conf.*.sink.prometheus.class":
            "org.apache.spark.metrics.sink.PrometheusServlet",
    }
```

### 7.2 Kubernetes SparkApplication CRD

```yaml
# bronze-kafka-ingestion.yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: bronze-kafka-ingestion
  namespace: data-pipelines
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster
  image: "my-registry/spark:3.5.0-python3.11"
  imagePullPolicy: Always

  mainApplicationFile: "s3a://spark-apps/bronze_kafka_ingestion.py"

  sparkVersion: "3.5.0"

  restartPolicy:
    type: OnFailure
    onFailureRetries: 3
    onFailureRetryInterval: 60  # seconds
    onSubmissionFailureRetries: 5
    onSubmissionFailureRetryInterval: 30

  driver:
    cores: 2
    coreLimit: "2000m"
    memory: "6g"
    memoryOverhead: "2g"

    labels:
      app: bronze-kafka-ingestion
      layer: bronze
      version: v2

    serviceAccount: spark-driver

    # Zone distribution
    affinity:
      nodeAffinity:
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values:
              - us-west-2a
              - us-west-2b
              - us-west-2c

    # Environment variables
    env:
    - name: AWS_REGION
      value: "us-west-2"
    - name: KAFKA_BROKERS
      valueFrom:
        configMapKeyRef:
          name: kafka-config
          key: brokers
    - name: CHECKPOINT_PATH
      value: "s3a://checkpoints/bronze/kafka-events"

    # Monitoring
    prometheus:
      jmxExporterJar: "/prometheus/jmx_prometheus_javaagent-0.17.0.jar"
      port: 8090

  executor:
    cores: 4
    coreLimit: "4000m"
    memory: "4g"
    memoryOverhead: "1g"
    instances: 10

    labels:
      app: bronze-kafka-ingestion
      layer: bronze
      version: v2

    # Zone distribution (same as driver)
    affinity:
      podAntiAffinity:
        preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - bronze-kafka-ingestion
            topologyKey: topology.kubernetes.io/zone

    # Local SSD for shuffle
    volumes:
    - name: spark-local-dir
      hostPath:
        path: /mnt/disks/ssd0
        type: Directory

    volumeMounts:
    - name: spark-local-dir
      mountPath: /tmp/spark-local

  # Dynamic allocation
  dynamicAllocation:
    enabled: true
    initialExecutors: 10
    minExecutors: 5
    maxExecutors: 50
    shuffleTrackingTimeout: 300  # seconds

  # Monitoring
  monitoring:
    exposeDriverMetrics: true
    exposeExecutorMetrics: true
    prometheus:
      jmxExporterJar: "/prometheus/jmx_prometheus_javaagent-0.17.0.jar"
      port: 8090

  # Spark configuration
  sparkConf:
    # (Use configurations from get_bronze_streaming_config())
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
    "spark.sql.streaming.checkpointLocation": "s3a://checkpoints/bronze/kafka-events"
    # ... (abbreviated for brevity, include all configs from Python function)

  # Dependencies
  deps:
    jars:
    - s3a://spark-jars/spark-sql-kafka-0-10_2.12-3.5.0.jar
    - s3a://spark-jars/delta-core_2.12-2.4.0.jar
    - s3a://spark-jars/kafka-clients-3.4.0.jar

    files:
    - s3a://spark-configs/log4j.properties
```

### 7.3 Argo Workflow for Gold Layer

```yaml
# gold-aggregation-workflow.yaml
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata:
  name: gold-aggregation
  namespace: data-pipelines
spec:
  schedule: "0 * * * *"  # Every hour
  timezone: "America/Los_Angeles"
  concurrencyPolicy: "Forbid"  # Prevent overlapping runs
  startingDeadlineSeconds: 300  # Fail if can't start within 5 min
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 3

  workflowSpec:
    entrypoint: gold-pipeline

    # Service account with S3 access
    serviceAccountName: spark-workflow

    # Failure handling
    onExit: cleanup-and-notify

    # Pod garbage collection
    podGC:
      strategy: OnPodSuccess

    # TTL after completion
    ttlStrategy:
      secondsAfterCompletion: 86400  # 24 hours
      secondsAfterSuccess: 3600  # 1 hour
      secondsAfterFailure: 604800  # 7 days

    templates:
    - name: gold-pipeline
      steps:
      - - name: validate-inputs
          template: validate-silver-data

      - - name: run-aggregation
          template: spark-job
          when: "{{steps.validate-inputs.outputs.result}} == success"

      - - name: optimize-tables
          template: optimize-delta
          when: "{{steps.run-aggregation.outputs.result}} == success"

      - - name: materialize-features
          template: feast-materialize
          when: "{{steps.optimize-tables.outputs.result}} == success"

      - - name: sync-to-warehouse
          template: snowflake-sync
          when: "{{steps.materialize-features.outputs.result}} == success"

    - name: validate-silver-data
      container:
        image: python:3.11-slim
        command: [python]
        args:
        - -c
        - |
          import boto3
          from datetime import datetime, timedelta

          # Check if last hour's Silver data exists
          s3 = boto3.client('s3')
          bucket = 'data-lake'
          prefix = f'silver/events/date={datetime.now().strftime("%Y-%m-%d")}'

          response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)

          if 'Contents' not in response:
              print("ERROR: No Silver data found for last hour")
              exit(1)

          print("SUCCESS: Silver data validated")
          exit(0)

      retryStrategy:
        limit: 3
        retryPolicy: "Always"
        backoff:
          duration: "30s"
          factor: 2

    - name: spark-job
      resource:
        action: create
        successCondition: status.applicationState.state == COMPLETED
        failureCondition: status.applicationState.state == FAILED
        manifest: |
          apiVersion: sparkoperator.k8s.io/v1beta2
          kind: SparkApplication
          metadata:
            name: gold-aggregation-{{workflow.creationTimestamp}}
            namespace: data-pipelines
          spec:
            type: Python
            pythonVersion: "3"
            mode: cluster
            image: "my-registry/spark:3.5.0-python3.11"
            mainApplicationFile: "s3a://spark-apps/gold_aggregation.py"

            arguments:
            - "--date={{workflow.parameters.date}}"
            - "--last-processed-version={{workflow.parameters.lastVersion}}"

            sparkVersion: "3.5.0"

            restartPolicy:
              type: Never

            driver:
              cores: 4
              memory: "16g"
              labels:
                app: gold-aggregation
                workflow: "{{workflow.name}}"
              serviceAccount: spark-driver

            executor:
              cores: 8
              memory: "16g"
              instances: 20
              labels:
                app: gold-aggregation
                workflow: "{{workflow.name}}"

            sparkConf:
              "spark.app.name": "gold-aggregation-{{workflow.creationTimestamp}}"
              # ... (other configs from get_gold_batch_config())

    - name: optimize-delta
      container:
        image: my-registry/delta-tools:latest
        command: [python]
        args:
        - -c
        - |
          from delta import DeltaTable
          from pyspark.sql import SparkSession

          spark = SparkSession.builder.appName("optimize-gold").getOrCreate()

          tables = [
              "s3a://data-lake/gold/daily_user_metrics",
              "s3a://data-lake/gold/regional_rollups"
          ]

          for table_path in tables:
              print(f"Optimizing {table_path}")
              dt = DeltaTable.forPath(spark, table_path)

              # Compact small files
              dt.optimize().executeCompaction()

              # Z-order
              dt.optimize().executeZOrderBy("user_id", "date")

              # Vacuum old files (> 30 days)
              dt.vacuum(retentionHours=720)

          print("All tables optimized")

      retryStrategy:
        limit: 2

    - name: feast-materialize
      container:
        image: my-registry/feast:latest
        command: [feast]
        args:
        - materialize-incremental
        - "{{workflow.parameters.date}}"

      env:
      - name: FEAST_REPO_PATH
        value: /feast-repo

      volumeMounts:
      - name: feast-config
        mountPath: /feast-repo

      retryStrategy:
        limit: 2

    - name: snowflake-sync
      container:
        image: my-registry/snowflake-sync:latest
        command: [python]
        args:
        - sync_to_snowflake.py
        - --date={{workflow.parameters.date}}

      envFrom:
      - secretRef:
          name: snowflake-credentials

      retryStrategy:
        limit: 3
        retryPolicy: "Always"

    - name: cleanup-and-notify
      container:
        image: curlimages/curl:latest
        command: [sh, -c]
        args:
        - |
          # Send Slack notification
          curl -X POST $SLACK_WEBHOOK_URL \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "Gold aggregation workflow completed",
              "attachments": [{
                "color": "{{workflow.status}}",
                "fields": [
                  {"title": "Workflow", "value": "{{workflow.name}}"},
                  {"title": "Status", "value": "{{workflow.status}}"},
                  {"title": "Duration", "value": "{{workflow.duration}}"}
                ]
              }]
            }'

      env:
      - name: SLACK_WEBHOOK_URL
        valueFrom:
          secretKeyRef:
            name: slack-webhook
            key: url

    # Volumes
    volumes:
    - name: feast-config
      configMap:
        name: feast-feature-repo

    # Parameters
    arguments:
      parameters:
      - name: date
        value: "{{workflow.creationTimestamp}}"
      - name: lastVersion
        value: "0"  # Will be updated dynamically
```

---

## 8. Self-Healing Mechanisms

### Summary of Self-Healing Features

| Layer | Failure Type | Detection Method | Recovery Action | RTO |
|-------|--------------|------------------|-----------------|-----|
| **Bronze** | Pod crash | Liveness probe | Restart + checkpoint resume | 2 min |
| **Bronze** | Bad records | Schema validation | Route to DLQ + alert | 1 min |
| **Bronze** | Kafka broker down | Connection timeout | Reconnect to other brokers | 30 sec |
| **Bronze** | Checkpoint corruption | Read failure | Fallback to previous checkpoint | 10 min |
| **Silver** | OOM | Container exit code | Increase memory + restart | 5 min |
| **Silver** | Enrichment failure | Exception | Use cached dimensions + alert | 1 min |
| **Silver** | Quality check failure | Great Expectations | Route to DLQ + continue | 1 min |
| **Gold** | Job timeout | Argo deadline | Cancel + retry next hour | 1 hour |
| **Gold** | MERGE conflict | Delta transaction conflict | Retry with exponential backoff | 5 min |
| **Kafka** | Consumer lag > 100K | Prometheus alert | Auto-scale consumers + 2 replicas | 10 min |
| **Executors** | Task failure | Spark DAG scheduler | Retry task on different executor (4x) | 2 min |
| **Zone** | Zone failure | Pod eviction | Reschedule in healthy zones | 3 min |
| **S3** | Throttling 503 | HTTP error code | Exponential backoff (1s → 16s) | 1 min |
| **Network** | Connection timeout | Socket timeout | Retry with new connection | 30 sec |

### 8.1 Automated Remediation Examples

**Example 1: High Memory Usage**

```python
# memory_monitor.py
"""Monitor executor memory and trigger auto-remediation"""

import prometheus_client
from kubernetes import client, config

def monitor_memory_usage():
    """Prometheus query for executor memory usage"""
    query = 'container_memory_working_set_bytes{pod=~"bronze-kafka-.*"} / ' \
            'container_spec_memory_limit_bytes{pod=~"bronze-kafka-.*"}'

    result = prometheus_client.query(query)

    for metric in result:
        pod_name = metric['metric']['pod']
        memory_pct = float(metric['value'][1])

        if memory_pct > 0.85:  # 85% threshold
            logger.warning(f"Pod {pod_name} memory usage: {memory_pct:.1%}")

            # Auto-remediation: Increase memory limit
            increase_pod_memory(pod_name, current_limit_gb=16, new_limit_gb=24)

def increase_pod_memory(pod_name, current_limit_gb, new_limit_gb):
    """Increase memory limit for a deployment"""
    config.load_incluster_config()
    apps_v1 = client.AppsV1Api()

    # Get deployment
    deployment = apps_v1.read_namespaced_deployment(
        name="bronze-kafka-ingestion",
        namespace="data-pipelines"
    )

    # Update memory limit
    for container in deployment.spec.template.spec.containers:
        if container.name == "spark-driver":
            container.resources.limits['memory'] = f"{new_limit_gb}Gi"
            container.resources.requests['memory'] = f"{new_limit_gb * 0.75}Gi"

    # Apply update (rolling restart)
    apps_v1.patch_namespaced_deployment(
        name="bronze-kafka-ingestion",
        namespace="data-pipelines",
        body=deployment
    )

    logger.info(f"Increased memory limit: {current_limit_gb}GB → {new_limit_gb}GB")
```

**Example 2: Kafka Lag Auto-Scaling**

```python
# kafka_lag_autoscaler.py
"""Scale Spark consumers based on Kafka lag"""

from kubernetes import client, config
import prometheus_client

def autoscale_based_on_lag():
    """Query Kafka lag and adjust replicas"""
    query = 'kafka_consumergroup_lag{group="spark-consumer-group-v1"}'
    result = prometheus_client.query(query)

    total_lag = sum(float(m['value'][1]) for m in result)

    # Scaling policy
    if total_lag > 500000:  # 500K messages
        target_replicas = 5
    elif total_lag > 200000:  # 200K messages
        target_replicas = 3
    elif total_lag > 100000:  # 100K messages
        target_replicas = 2
    else:
        target_replicas = 1

    # Apply scaling
    scale_deployment("bronze-kafka-ingestion", "data-pipelines", target_replicas)

def scale_deployment(name, namespace, replicas):
    """Scale a Kubernetes deployment"""
    config.load_incluster_config()
    apps_v1 = client.AppsV1Api()

    # Get current scale
    scale = apps_v1.read_namespaced_deployment_scale(name, namespace)
    current_replicas = scale.spec.replicas

    if current_replicas != replicas:
        scale.spec.replicas = replicas
        apps_v1.patch_namespaced_deployment_scale(name, namespace, scale)
        logger.info(f"Scaled {name}: {current_replicas} → {replicas} replicas")
```

---

## 9. Deployment Architecture

### 9.1 Kubernetes Cluster Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (EKS/GKE/AKS)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  NAMESPACES:                                                                 │
│  ├─ data-pipelines         (Spark jobs, workflows)                           │
│  ├─ kafka                   (Kafka brokers, ZooKeeper)                       │
│  ├─ monitoring              (Prometheus, Grafana, Loki)                      │
│  ├─ operators               (Spark Operator, Argo, KEDA)                     │
│  └─ istio-system            (Service mesh control plane)                     │
│                                                                               │
│  NODE POOLS:                                                                 │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ SYSTEM POOL (3 nodes, t3.large)                            │             │
│  ├────────────────────────────────────────────────────────────┤             │
│  │ • Kubernetes control plane components                      │             │
│  │ • Monitoring stack (Prometheus, Grafana)                   │             │
│  │ • Operators (Spark, Argo, KEDA)                            │             │
│  │ • Taint: system=true:NoSchedule                            │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ SPARK DRIVER POOL (3 nodes, m5.2xlarge)                    │             │
│  ├────────────────────────────────────────────────────────────┤             │
│  │ • Spark drivers (8 vCPU, 32 GB RAM each)                   │             │
│  │ • Label: spark-role=driver                                 │             │
│  │ • Taint: spark-driver=true:NoSchedule                      │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ SPARK EXECUTOR POOL (10-50 nodes, m5.4xlarge)              │             │
│  ├────────────────────────────────────────────────────────────┤             │
│  │ • Spark executors (16 vCPU, 64 GB RAM each)                │             │
│  │ • Autoscaling: enabled (10 min, 50 max)                    │             │
│  │ • Label: spark-role=executor                               │             │
│  │ • Local NVMe SSD for shuffle (1 TB)                        │             │
│  │ • Spot instances: 70% (fallback to on-demand)              │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │ KAFKA POOL (3 nodes, r5.2xlarge)                           │             │
│  ├────────────────────────────────────────────────────────────┤             │
│  │ • Kafka brokers (8 vCPU, 64 GB RAM each)                   │             │
│  │ • EBS volumes: 2 TB SSD (gp3, 10K IOPS)                    │             │
│  │ • Label: kafka=true                                        │             │
│  │ • Taint: kafka=true:NoSchedule                             │             │
│  │ • Anti-affinity: one broker per zone                       │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                               │
│  NETWORKING:                                                                 │
│  ├─ CNI: Calico (network policy enforcement)                                │
│  ├─ Service Mesh: Istio (mTLS, observability)                               │
│  ├─ Ingress: Istio Gateway + AWS ALB                                        │
│  └─ DNS: CoreDNS with caching                                               │
│                                                                               │
│  STORAGE:                                                                    │
│  ├─ CSI Driver: EBS CSI (dynamic provisioning)                              │
│  ├─ Storage Classes: gp3 (default), io2 (high IOPS)                         │
│  └─ External: S3 (Delta Lake, checkpoints)                                  │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 GitOps Deployment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GITOPS DEPLOYMENT FLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  1. DEVELOPER WORKFLOW                                                       │
│     ┌──────────────────────────────────────────────────┐                    │
│     │ Developer                                         │                    │
│     │  ↓                                                │                    │
│     │ 1. Make changes to Spark job code                │                    │
│     │ 2. Update SparkApplication YAML                  │                    │
│     │ 3. Commit to feature branch                      │                    │
│     │ 4. Open pull request                             │                    │
│     └────────────────────┬─────────────────────────────┘                    │
│                          ↓                                                    │
│  2. CI PIPELINE (GitHub Actions)                                             │
│     ┌──────────────────────────────────────────────────┐                    │
│     │ Pull Request Checks                              │                    │
│     │  ↓                                                │                    │
│     │ 1. Lint code (pylint, black)                     │                    │
│     │ 2. Run unit tests (pytest)                       │                    │
│     │ 3. Build Docker image                            │                    │
│     │ 4. Push to ECR (tag: PR-123)                     │                    │
│     │ 5. Deploy to DEV cluster (Argo CD)               │                    │
│     │ 6. Run integration tests                         │                    │
│     │ 7. Report results to PR                          │                    │
│     └────────────────────┬─────────────────────────────┘                    │
│                          ↓                                                    │
│  3. MERGE TO MAIN                                                            │
│     ┌──────────────────────────────────────────────────┐                    │
│     │ Main Branch CI                                   │                    │
│     │  ↓                                                │                    │
│     │ 1. Build production image                        │                    │
│     │ 2. Tag: main-abc123, v2.3.4                      │                    │
│     │ 3. Push to ECR                                   │                    │
│     │ 4. Update image tag in manifests/prod/           │                    │
│     │ 5. Commit manifest change                        │                    │
│     └────────────────────┬─────────────────────────────┘                    │
│                          ↓                                                    │
│  4. ARGO CD SYNC (Production)                                                │
│     ┌──────────────────────────────────────────────────┐                    │
│     │ Argo CD Application                              │                    │
│     │  ↓                                                │                    │
│     │ 1. Detect manifest change                        │                    │
│     │ 2. Diff current vs desired state                 │                    │
│     │ 3. Sync strategy: Rolling update                 │                    │
│     │ 4. Health check: Spark driver ready              │                    │
│     │ 5. Mark as "Synced" and "Healthy"                │                    │
│     │ 6. Send notification to Slack                    │                    │
│     └────────────────────┬─────────────────────────────┘                    │
│                          ↓                                                    │
│  5. ROLLBACK (if needed)                                                     │
│     ┌──────────────────────────────────────────────────┐                    │
│     │ Automated or Manual Rollback                     │                    │
│     │  ↓                                                │                    │
│     │ 1. Detect failed health check                    │                    │
│     │ 2. Argo CD auto-rollback to previous version     │                    │
│     │ 3. Alert PagerDuty                               │                    │
│     │ 4. Create incident ticket                        │                    │
│     └──────────────────────────────────────────────────┘                    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

DIRECTORY STRUCTURE:
├── spark-jobs/
│   ├── bronze/
│   │   ├── kafka_ingestion.py
│   │   └── s3_batch_ingestion.py
│   ├── silver/
│   │   ├── cleansing.py
│   │   └── enrichment.py
│   └── gold/
│       └── aggregation.py
│
├── manifests/
│   ├── base/
│   │   ├── spark-operator.yaml
│   │   ├── kafka.yaml
│   │   └── monitoring.yaml
│   │
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patches/
│   │
│   └── prod/
│       ├── kustomization.yaml
│       ├── bronze-kafka-ingestion.yaml
│       ├── silver-enrichment.yaml
│       └── gold-aggregation-workflow.yaml
│
└── .github/
    └── workflows/
        ├── ci-spark-jobs.yaml
        └── cd-manifests.yaml
```

---

## 10. Monitoring & Observability

### 10.1 Metrics (Prometheus)

**Key Metrics**:

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `spark_streaming_processed_rows_total` | Counter | Total rows processed | Rate < 100/sec for 10min |
| `spark_streaming_lag_seconds` | Gauge | Processing lag (event time - processing time) | > 300 sec for 5min |
| `kafka_consumergroup_lag` | Gauge | Kafka consumer lag (messages) | > 100K for 5min |
| `spark_executor_memory_used_bytes` | Gauge | Executor memory usage | > 85% for 5min |
| `spark_driver_jvm_heap_used` | Gauge | Driver heap usage | > 90% for 5min |
| `spark_application_status` | Gauge | Application status (0=failed, 1=running) | == 0 |
| `delta_table_size_bytes` | Gauge | Delta table size | Growth > 2x/day |
| `spark_task_failed_total` | Counter | Failed tasks | Rate > 10/min |
| `argo_workflow_status` | Gauge | Workflow status | == FAILED |
| `checkpoint_age_seconds` | Gauge | Time since last checkpoint | > 600 sec |

**Prometheus Alerts**:

```yaml
# prometheus-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: spark-pipeline-alerts
  namespace: monitoring
spec:
  groups:
  - name: streaming
    interval: 30s
    rules:
    - alert: SparkStreamingLagHigh
      expr: spark_streaming_lag_seconds > 300
      for: 5m
      labels:
        severity: warning
        component: spark
      annotations:
        summary: "Spark streaming lag is high"
        description: "Job {{ $labels.job }} has lag of {{ $value }} seconds"

    - alert: KafkaConsumerLagCritical
      expr: kafka_consumergroup_lag{group="spark-consumer-group-v1"} > 500000
      for: 5m
      labels:
        severity: critical
        component: kafka
      annotations:
        summary: "Kafka consumer lag is critical"
        description: "Consumer group has lag of {{ $value }} messages"

    - alert: SparkExecutorOOMRisk
      expr: (spark_executor_memory_used_bytes / spark_executor_memory_max_bytes) > 0.85
      for: 5m
      labels:
        severity: warning
        component: spark
      annotations:
        summary: "Spark executor memory usage high"
        description: "Executor {{ $labels.executor_id }} using {{ $value | humanizePercentage }} memory"

    - alert: SparkApplicationFailed
      expr: spark_application_status == 0
      for: 1m
      labels:
        severity: critical
        component: spark
      annotations:
        summary: "Spark application failed"
        description: "Application {{ $labels.application_name }} has failed"

  - name: batch
    interval: 1m
    rules:
    - alert: ArgoWorkflowFailed
      expr: argo_workflow_status{phase="Failed"} == 1
      for: 1m
      labels:
        severity: critical
        component: argo
      annotations:
        summary: "Argo workflow failed"
        description: "Workflow {{ $labels.name }} has failed"

    - alert: GoldAggregationMissed
      expr: time() - argo_workflow_completion_time{name="gold-aggregation"} > 7200
      for: 5m
      labels:
        severity: critical
        component: gold
      annotations:
        summary: "Gold aggregation hasn't run in 2 hours"
        description: "Last run: {{ $value | humanizeDuration }} ago"
```

### 10.2 Logs (Loki)

**Log Aggregation**:

```yaml
# promtail-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080

    positions:
      filename: /tmp/positions.yaml

    clients:
      - url: http://loki:3100/loki/api/v1/push

    scrape_configs:
    # Spark driver logs
    - job_name: spark-driver
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_spark_role]
        regex: driver
        action: keep
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      pipeline_stages:
      - regex:
          expression: '(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.*)'
      - labels:
          level:
      - timestamp:
          source: timestamp
          format: '2006-01-02 15:04:05'

    # Spark executor logs
    - job_name: spark-executor
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_spark_role]
        regex: executor
        action: keep
      pipeline_stages:
      - regex:
          expression: '(?P<level>\w+) (?P<message>.*)'
      - labels:
          level:
```

**LogQL Queries**:

```
# View all errors from Bronze layer
{namespace="data-pipelines", app="bronze-kafka-ingestion"} |= "ERROR"

# Track checkpoint recovery
{namespace="data-pipelines"} |= "Recovering from checkpoint"

# Monitor OOM events
{namespace="data-pipelines"} |= "OutOfMemoryError"

# Track processing rates
rate({namespace="data-pipelines", app="bronze-kafka-ingestion"} |= "Processed" [5m])
```

### 10.3 Traces (Jaeger)

**Distributed Tracing**:

```python
# Add tracing to Spark job
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent.monitoring.svc.cluster.local",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Instrument Spark job
with tracer.start_as_current_span("bronze_kafka_ingestion"):
    with tracer.start_as_current_span("read_kafka"):
        kafka_stream = spark.readStream.format("kafka").load()

    with tracer.start_as_current_span("validate_schema"):
        validated_df = kafka_stream.filter(...)

    with tracer.start_as_current_span("write_delta"):
        query = validated_df.writeStream.format("delta").start()
```

### 10.4 Dashboards (Grafana)

**Bronze Layer Dashboard**:

```
┌─────────────────────────────────────────────────────────────┐
│ Bronze Layer - Kafka Ingestion                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Processing Rate]         [Kafka Lag]        [Errors]      │
│   12.5K rows/sec            45K messages       3 errors/hr  │
│   ▲ 15% from avg           ▼ 20% from peak     ✓ Normal    │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Throughput (rows/sec)                                 │ │
│  │                                                       │ │
│  │  15K ┤                         ╭─╮                   │ │
│  │  12K ┤       ╭─╮     ╭─────────╯ ╰──╮                │ │
│  │   9K ┤   ╭───╯ ╰─────╯                ╰──╮            │ │
│  │   6K ┤───╯                                ╰───        │ │
│  │      └────────────────────────────────────────────   │ │
│  │       12:00    13:00    14:00    15:00    16:00      │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐ ┌──────────────────────────────┐ │
│  │ Consumer Lag         │ │ Executor Health              │ │
│  │                      │ │                              │ │
│  │ Partition 0: 12.3K   │ │ ● executor-1: Healthy (4GB)  │ │
│  │ Partition 1: 11.8K   │ │ ● executor-2: Healthy (3.8GB)│ │
│  │ Partition 2: 13.1K   │ │ ● executor-3: Warning (7.2GB)│ │
│  │ ...                  │ │ ...                          │ │
│  └──────────────────────┘ └──────────────────────────────┘ │
│                                                              │
│  [Recent Errors]                                            │
│  • 14:23:45 - Schema validation failed (user_id null)       │
│  • 14:15:32 - Checkpoint retry (S3 throttling)              │
│  • 14:08:12 - Executor lost (zone-a node failure)           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Summary & Design Rationale

### Key Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Medallion Architecture** | Clear separation of concerns, incremental quality improvement | More storage (3 copies of data) |
| **Delta Lake** | ACID transactions, time travel, schema evolution | Vendor lock-in (Databricks ecosystem) |
| **RocksDB State Store** | Low-latency state access for streaming | Requires local SSD, more complex ops |
| **Kubernetes** | Portability, auto-scaling, self-healing | Operational complexity |
| **Spark Operator** | Declarative job management, native K8s integration | Additional dependency |
| **Argo Workflows** | Powerful DAG orchestration, Cron scheduling | Learning curve |
| **Exactly-once semantics** | Data integrity, no duplicates/losses | Higher latency (checkpointing overhead) |
| **Multi-zone deployment** | High availability, fault tolerance | Cross-zone network costs |
| **GitOps (Argo CD)** | Version control for infra, audit trail | Requires discipline in manifest management |
| **Prometheus + Grafana** | Industry-standard, rich ecosystem | High cardinality can cause issues |

### Self-Healing Capabilities Summary

1. **Automatic pod restart** (Kubernetes liveness probes)
2. **Checkpoint-based recovery** (Spark Structured Streaming)
3. **Exactly-once processing** (Delta + Kafka coordination)
4. **Dead letter queues** (isolate bad data, continue processing)
5. **Dynamic resource allocation** (scale executors based on load)
6. **Multi-zone distribution** (tolerate zone failures)
7. **Adaptive backpressure** (prevent overwhelming downstream)
8. **Quality gates** (Great Expectations validation)
9. **Leader election** (singleton components like operators)
10. **Automated remediation** (memory scaling, lag-based autoscaling)

### Performance Characteristics

| Metric | Target | Typical | Notes |
|--------|--------|---------|-------|
| **End-to-end latency** | < 2 min | 80 sec | Kafka → Bronze → Silver |
| **Throughput** | 10K msg/sec | 12K msg/sec | Kafka ingestion |
| **Recovery time (pod crash)** | < 5 min | 3 min | Including checkpoint restore |
| **Recovery time (zone failure)** | < 10 min | 8 min | Pod rescheduling + restore |
| **Data freshness (Gold)** | Hourly | 20 min lag | Batch job processing time |
| **Query latency (Gold)** | < 10 sec | 5 sec | Typical analytics query |
| **Checkpoint overhead** | < 5% | 3% | Processing time increase |

### Cost Optimization

1. **Spot instances** for Spark executors (70% cost savings)
2. **Dynamic allocation** (scale to zero when idle)
3. **S3 Intelligent-Tiering** (automatic archival)
4. **Delta VACUUM** (delete old files after 30 days)
5. **Z-ordering** (reduce query scan size by 50%)
6. **Kafka retention** (7 days, replay from Delta if needed)
7. **Executor right-sizing** (profiling-driven optimization)

---

## Appendix A: Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Compute** | Apache Spark | 3.5.0 | Distributed processing |
| **Storage** | Delta Lake | 2.4.0 | ACID data lake |
| **Messaging** | Apache Kafka | 3.4.0 | Event streaming |
| **Orchestration** | Argo Workflows | 3.4.0 | DAG scheduling |
| **Container Platform** | Kubernetes | 1.28 | Container orchestration |
| **Operator** | Spark Operator | 1.3.0 | Spark job management |
| **Service Mesh** | Istio | 1.18.0 | mTLS, observability |
| **Monitoring** | Prometheus | 2.45.0 | Metrics collection |
| **Logging** | Loki | 2.8.0 | Log aggregation |
| **Tracing** | Jaeger | 1.47.0 | Distributed tracing |
| **Dashboards** | Grafana | 10.0.0 | Visualization |
| **GitOps** | Argo CD | 2.7.0 | Declarative deployment |
| **Autoscaling** | KEDA | 2.11.0 | Event-driven autoscaling |
| **Secrets** | External Secrets Operator | 0.9.0 | Secret management |
| **Data Quality** | Great Expectations | 0.17.0 | Validation framework |
| **Feature Store** | Feast | 0.32.0 | ML feature serving |

---

## Appendix B: References

1. **Delta Lake Documentation**: https://docs.delta.io/
2. **Spark Structured Streaming Guide**: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
3. **Kubernetes Best Practices**: https://kubernetes.io/docs/concepts/configuration/overview/
4. **Spark Operator**: https://github.com/GoogleCloudPlatform/spark-on-k8s-operator
5. **Argo Workflows**: https://argoproj.github.io/argo-workflows/
6. **Great Expectations**: https://docs.greatexpectations.io/
7. **Medallion Architecture**: https://www.databricks.com/glossary/medallion-architecture

---

**Document Status**: ✅ Complete
**Review Status**: Pending architecture review
**Next Steps**: Implementation phase [I]

---

*This design document provides a comprehensive blueprint for building a production-ready, self-healing Apache Spark data pipeline on Kubernetes. All architectural decisions are justified with clear rationale, and the system is designed for operational excellence from day one.*
