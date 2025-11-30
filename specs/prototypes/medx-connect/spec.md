# MedX Connect - Prototype Spec

## The Core Bet

> **If a lab can submit results that reach a doctor in < 5 minutes (vs. fax/call), and a pharmacy can receive Rx in < 30 seconds, they will adopt.**

---

## Success Criteria (4 Weeks)

| # | Metric | Target | How to Measure |
|---|--------|--------|----------------|
| 1 | Lab result delivery | < 5 min | Timestamp from submit to doctor notification |
| 2 | Rx transmission | < 30 sec | Timestamp from doctor send to pharmacy receive |
| 3 | Data accuracy | 100% | What lab enters = what doctor sees |
| 4 | Partner adoption | 3 each | 3 labs + 3 pharmacies + 3 doctors test it |
| 5 | Error rate | < 1% | Failed deliveries / total deliveries |

---

## What We're Building (Only This)

```
┌─────────────────────────────────────────────────────┐
│                  MedX Connect MVP                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  LAB PORTAL              CENTRAL              DOCTOR │
│  (Web Form)              (REST API)           (App)  │
│                                                      │
│  ┌──────────┐         ┌───────────┐      ┌────────┐ │
│  │ Enter    │         │           │      │ View   │ │
│  │ Results  │────────▶│  Simple   │─────▶│ Results│ │
│  │ Form     │         │  Database │      │ Alert  │ │
│  └──────────┘         │           │      └────────┘ │
│                       │ PostgreSQL│                  │
│  ┌──────────┐         │           │      ┌────────┐ │
│  │ Receive  │         │           │      │ Send   │ │
│  │ Rx       │◀────────│           │◀─────│ Rx     │ │
│  │ Alert    │         │           │      │ Form   │ │
│  └──────────┘         └───────────┘      └────────┘ │
│  PHARMACY                                            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 5 Deliverables

### Week 1: Lab Portal
- [ ] **D1**: Simple web form for lab results entry
- [ ] **D2**: Fields: Patient name, DOB, test type, values, units, reference range
- [ ] **D3**: Submit → stored in database

### Week 2: Doctor View
- [ ] **D4**: Doctor dashboard showing pending results
- [ ] **D5**: Push notification when new result arrives
- [ ] **D6**: Mark as reviewed

### Week 3: Pharmacy Flow
- [ ] **D7**: Doctor can send Rx (medication, dose, quantity, patient)
- [ ] **D8**: Pharmacy portal shows incoming prescriptions
- [ ] **D9**: Pharmacy confirms receipt

### Week 4: Test & Measure
- [ ] **D10**: Run 50 test transactions
- [ ] **D11**: Measure delivery times
- [ ] **D12**: GO/NO-GO decision

---

## What We're NOT Building

| Feature | Why Not |
|---------|---------|
| ❌ HL7/FHIR integration | Web forms are faster to build |
| ❌ Automated lab machine integration | Manual entry first |
| ❌ Insurance/billing | Out of scope |
| ❌ Controlled substance tracking | Regulatory complexity |
| ❌ Multi-tenant architecture | Single instance for prototype |
| ❌ Mobile apps for labs/pharmacies | Web-only for MVP |

---

## Tech Stack (Simple)

```yaml
Frontend:
  - React (Create React App)
  - Simple forms, no fancy UI

Backend:
  - Node.js + Express
  - PostgreSQL (Supabase free tier)
  - REST API

Notifications:
  - Email (SendGrid free tier)
  - Or just polling the dashboard

Auth:
  - Simple email/password
  - No SSO for prototype

Hosting:
  - Vercel (free)
  - Supabase (free)
```

**Monthly Cost: ~$0-20** (free tiers)

---

## Data Model (Minimal)

```sql
-- Entities
labs (id, name, email, password_hash)
pharmacies (id, name, email, password_hash)
doctors (id, name, email, password_hash)

-- Lab Results
lab_results (
  id, lab_id, doctor_id,
  patient_name, patient_dob,
  test_type, test_value, units, reference_range,
  submitted_at, viewed_at
)

-- Prescriptions
prescriptions (
  id, doctor_id, pharmacy_id,
  patient_name, patient_dob,
  medication, dose, quantity, instructions,
  sent_at, received_at
)
```

---

## GO / NO-GO Decision (Week 4)

### GO ✅ if:
- [ ] Lab → Doctor delivery consistently < 5 min
- [ ] Doctor → Pharmacy delivery < 30 sec
- [ ] 3/3 labs say "easier than fax"
- [ ] 3/3 pharmacies say "clearer than phone calls"
- [ ] Zero data corruption in 50 test transactions

### NO-GO ❌ if:
- [ ] Labs won't use web form ("too much typing")
- [ ] Doctors don't check the dashboard
- [ ] Pharmacies prefer phone calls

### Pivot Options if NO-GO:
1. **Narrower**: Just lab results, no pharmacy
2. **Different entry**: Photo/scan of printed results
3. **Push harder**: SMS alerts instead of dashboard

---

## The One Question

> **"Is this faster than your current process (fax/phone)?"**

If 8/9 partners say yes → **GO**
If they say "about the same" → **Find the friction**
