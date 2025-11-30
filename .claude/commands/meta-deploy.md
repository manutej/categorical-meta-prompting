---
description: Orchestrated deployment workflow - validate, stage, deploy, verify with rollback support
allowed-tools: Read, Write, Edit, Bash(*), Grep, Glob, TodoWrite
argument-hint: [deployment-target]
---

# Meta-Deploy: Orchestrated Safe Deployment

Deploy with full orchestration including validation, staging, and automatic rollback.

## Deployment Target
$ARGUMENTS

---

## Orchestration Plan

```
@orchestration
  @sequential[

    ═══════════════════════════════════════════════════════
    STAGE 1: PRE-DEPLOYMENT VALIDATION
    ═══════════════════════════════════════════════════════

    @parallel[
      → /meta-test ${target}
      → /meta-review ${target}
      → Check deployment prerequisites
    ]
    # All validation in parallel for speed

    ◆ tests:pass
    ◆ review:approved
    ◆ prerequisites:met

    ═══════════════════════════════════════════════════════
    STAGE 2: BUILD & PACKAGE
    ═══════════════════════════════════════════════════════

    @run:now
    → Build production artifacts

    @run:now
    → Verify build integrity

    ◆ build:success
    ◆ artifacts:verified

    ═══════════════════════════════════════════════════════
    STAGE 3: STAGING DEPLOYMENT
    ═══════════════════════════════════════════════════════

    @run:now
    → Deploy to staging environment

    @timeout:300s
    → Run staging smoke tests

    @if:smoke_tests:fail
      @run:now
      → Rollback staging
      → /debug ${failures}
      → ABORT deployment

    ◆ staging:healthy

    ═══════════════════════════════════════════════════════
    STAGE 4: PRODUCTION DEPLOYMENT
    ═══════════════════════════════════════════════════════

    @run:now
    → Capture production state (for rollback)

    @run:now
    → Deploy to production

    @timeout:60s
    → Health check production

    @if:health_check:fail
      @run:now
      → Automatic rollback
      → /debug ${failure}
      → ALERT: deployment failed

    ◆ production:healthy

    ═══════════════════════════════════════════════════════
    STAGE 5: POST-DEPLOYMENT VERIFICATION
    ═══════════════════════════════════════════════════════

    @parallel[
      → Monitor error rates
      → Verify key metrics
      → Run production smoke tests
    ]

    @timeout:600s
    @if:anomaly:detected
      @fallback:rollback
        → Rollback production
        → /debug ${anomaly}

    ◆ metrics:normal
    ◆ no:anomalies

    ═══════════════════════════════════════════════════════
    STAGE 6: FINALIZE
    ═══════════════════════════════════════════════════════

    @run:now
    → Tag release
    → Update deployment records
    → Notify stakeholders

    ◆ deployment:complete

  ]
@end
```

---

## Execution Trace

### Stage 1: Pre-Deployment Validation

```
@parallel[
┌───────────────────┬───────────────────┬───────────────────┐
│ /meta-test        │ /meta-review      │ PREREQUISITES     │
├───────────────────┼───────────────────┼───────────────────┤
│                   │                   │                   │
│ Running full      │ Running multi-    │ Checking:         │
│ test suite...     │ pass review...    │                   │
│                   │                   │ □ Credentials     │
│ Unit: [status]    │ Correctness: /10  │ □ Permissions     │
│ Integration: []   │ Security: /10     │ □ Dependencies    │
│ Property: []      │ Performance: /10  │ □ Config          │
│                   │                   │ □ Resources       │
│                   │                   │                   │
│ Overall: [P/F]    │ Overall: [P/F]    │ Overall: [P/F]    │
└───────────────────┴───────────────────┴───────────────────┘
]
```

**Validation Gate:**
| Check | Status | Details |
|-------|--------|---------|
| Tests | | |
| Review | | |
| Prerequisites | | |

---

### Stage 2: Build & Package

```
┌─────────────────────────────────────────────┐
│ @run:now → Build production artifacts       │
│                                             │
│ Build Command: [command]                    │
│ Build Output: [location]                    │
│                                             │
│ Artifacts:                                  │
│ - [artifact 1]: [size] [checksum]           │
│ - [artifact 2]: [size] [checksum]           │
│                                             │
│ Build Status: [SUCCESS/FAILED]              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ @run:now → Verify build integrity           │
│                                             │
│ Checks:                                     │
│ ✓ Checksums match                           │
│ ✓ No sensitive data in artifacts            │
│ ✓ Dependencies bundled correctly            │
│ ✓ Configuration for target environment      │
│                                             │
│ Integrity: [VERIFIED/FAILED]                │
└─────────────────────────────────────────────┘
```

---

### Stage 3: Staging Deployment

```
┌─────────────────────────────────────────────┐
│ @run:now → Deploy to staging                │
│                                             │
│ Target: [staging environment URL/ID]        │
│ Method: [deployment method]                 │
│                                             │
│ Progress:                                   │
│ [████████████████████░░░░] 80%              │
│                                             │
│ Status: [DEPLOYING/COMPLETE/FAILED]         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ @timeout:300s → Smoke tests                 │
│                                             │
│ Running smoke tests against staging...      │
│                                             │
│ □ Health endpoint                           │
│ □ Authentication flow                       │
│ □ Core functionality                        │
│ □ Database connectivity                     │
│ □ External service connectivity             │
│                                             │
│ Time elapsed: [X]s / 300s                   │
│ Status: [RUNNING/PASS/FAIL]                 │
└─────────────────────────────────────────────┘

@if:smoke_tests:fail
┌─────────────────────────────────────────────┐
│ ⚠️  SMOKE TESTS FAILED                       │
│                                             │
│ → Rollback staging                          │
│ → /debug ${failures}                        │
│ → ABORT deployment                          │
│                                             │
│ Failure reason: [reason]                    │
└─────────────────────────────────────────────┘
```

---

### Stage 4: Production Deployment

```
┌─────────────────────────────────────────────┐
│ @run:now → Capture production state         │
│                                             │
│ Rollback snapshot created:                  │
│ - Snapshot ID: [id]                         │
│ - Timestamp: [time]                         │
│ - Version: [current version]                │
│                                             │
│ Rollback command: [command to rollback]     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ @run:now → Deploy to production             │
│                                             │
│ Target: [production environment]            │
│ Strategy: [rolling/blue-green/canary]       │
│                                             │
│ Progress:                                   │
│ [████████████████████████] 100%             │
│                                             │
│ Status: [DEPLOYING/COMPLETE/FAILED]         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ @timeout:60s → Health check                 │
│                                             │
│ Checking production health...               │
│                                             │
│ ✓ Application responding                    │
│ ✓ Database connected                        │
│ ✓ Services reachable                        │
│ ✓ No error spike                            │
│                                             │
│ Health: [HEALTHY/UNHEALTHY]                 │
└─────────────────────────────────────────────┘

@if:health_check:fail
┌─────────────────────────────────────────────┐
│ 🚨 HEALTH CHECK FAILED - AUTO ROLLBACK      │
│                                             │
│ → Automatic rollback initiated              │
│ → Restoring snapshot: [id]                  │
│ → /debug ${failure}                         │
│                                             │
│ Rollback status: [IN PROGRESS]              │
│ Alert sent to: [stakeholders]               │
└─────────────────────────────────────────────┘
```

---

### Stage 5: Post-Deployment Verification

```
@parallel[
┌───────────────────┬───────────────────┬───────────────────┐
│ ERROR RATES       │ KEY METRICS       │ SMOKE TESTS       │
├───────────────────┼───────────────────┼───────────────────┤
│                   │                   │                   │
│ Monitoring for    │ Comparing:        │ Production        │
│ 10 minutes...     │                   │ smoke tests:      │
│                   │ - Latency         │                   │
│ Error rate:       │ - Throughput      │ ✓ Test 1          │
│ Before: [X]%      │ - Memory          │ ✓ Test 2          │
│ After: [Y]%       │ - CPU             │ ✓ Test 3          │
│                   │                   │                   │
│ Δ: [change]       │ Status: [OK]      │ All: [PASS]       │
└───────────────────┴───────────────────┴───────────────────┘
]

@timeout:600s
@if:anomaly:detected
┌─────────────────────────────────────────────┐
│ ⚠️  ANOMALY DETECTED                         │
│                                             │
│ Type: [error spike / latency increase / ...]│
│ Severity: [critical / warning]              │
│                                             │
│ @fallback:rollback                          │
│ → Rollback production                       │
│ → /debug ${anomaly}                         │
└─────────────────────────────────────────────┘
```

---

### Stage 6: Finalize

```
┌─────────────────────────────────────────────┐
│ @run:now → Finalize deployment              │
│                                             │
│ ✓ Release tagged: v[X.Y.Z]                  │
│ ✓ Deployment record updated                 │
│ ✓ Changelog generated                       │
│ ✓ Stakeholders notified                     │
│                                             │
│ Deployment ID: [id]                         │
│ Duration: [total time]                      │
│ Status: COMPLETE                            │
└─────────────────────────────────────────────┘
```

---

## Deployment Summary

| Stage | Status | Duration | Notes |
|-------|--------|----------|-------|
| Validation | | | |
| Build | | | |
| Staging | | | |
| Production | | | |
| Verification | | | |
| Finalize | | | |

**Deployment Result:** [SUCCESS / ROLLED BACK / FAILED]

**Version:**
- Previous: [old version]
- Current: [new version]

**Rollback Available:** Yes - Snapshot [id]

**Commands Invoked:**
- /meta-test (validation)
- /meta-review (validation)
- /debug (if failures)

**Notifications Sent:**
- [stakeholder list]
