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

## STAGE 1: Pre-Deployment Validation

**ACTION: Validate everything in parallel before deployment**

### 1A. Run Tests (/meta-test)
```bash
Command: [test command]
```
| Type | Passed | Failed |
|------|--------|--------|
| Unit | | |
| Integration | | |
| Property | | |

### 1B. Run Review (/meta-review)
| Dimension | Score |
|-----------|-------|
| Correctness | /10 |
| Security | /10 |
| Performance | /10 |

### 1C. Check Prerequisites
| Prerequisite | Status | Notes |
|--------------|--------|-------|
| Credentials available | ✓/✗ | |
| Permissions granted | ✓/✗ | |
| Config files ready | ✓/✗ | |
| Dependencies resolved | ✓/✗ | |
| Target environment accessible | ✓/✗ | |

**ABORT CONDITIONS:**
- Any test fails → Fix before deploying
- Security issues found → Remediate first
- Missing credentials → Cannot proceed
- Environment unreachable → Check connectivity

---

## STAGE 2: Build & Package

**ACTION: Create production artifacts**

```bash
Build command: [e.g., npm run build, docker build, go build]
Output location: [path/to/artifacts]
```

**Build Results:**
| Artifact | Size | Checksum |
|----------|------|----------|
| [artifact name] | [size] | [sha256] |

**Integrity Checks:**
| Check | Status |
|-------|--------|
| Checksums verified | ✓/✗ |
| No secrets in artifacts | ✓/✗ |
| Dependencies bundled | ✓/✗ |
| Correct environment config | ✓/✗ |

**Build Status:** [SUCCESS / FAILED]

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
| 1. Validation | | | |
| 2. Build | | | |
| 3. Staging | | | |
| 4. Production | | | |
| 5. Verification | | | |
| 6. Finalize | | | |

**Result:** [SUCCESS / ROLLED BACK / FAILED]

**Version Change:**
| | Value |
|----------|-------|
| Previous | [vX.Y.Z] |
| Current | [vX.Y.Z] |

**Rollback Info:**
```
Snapshot ID: [id]
Rollback command: [command to execute rollback]
```

**Commands Used:**
- /meta-test (validation)
- /meta-review (validation)
- /debug (if any failures)

**Notifications:**
- [ ] Team notified
- [ ] Stakeholders informed
- [ ] Release notes published
