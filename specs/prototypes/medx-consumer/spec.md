# MedX Consumer - Prototype Spec

## The Core Bet

> **If a patient can pull their records from 2 sources and share with a new doctor in under 2 minutes, they'll use it for every new provider visit.**

---

## Success Criteria (4 Weeks)

| # | Metric | Target | How to Measure |
|---|--------|--------|----------------|
| 1 | Record aggregation | 2+ sources | Patient connects lab + pharmacy in one session |
| 2 | Share time | < 2 min | Timer from "share" tap to doctor receiving link |
| 3 | Doctor access | Works | Doctor opens link, sees patient summary |
| 4 | Patient adoption | 10 users | Friends/family complete full flow |
| 5 | Data accuracy | 100% | What patient entered = what doctor sees |

---

## What We're Building (Only This)

```
┌─────────────────────────────────────────────────────┐
│                   MedX Consumer                      │
│                   (Mobile PWA)                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│   ┌─────────────┐      ┌─────────────────────┐      │
│   │   Manual    │      │    My Profile       │      │
│   │   Entry     │─────▶│  (SQLite/Local)     │      │
│   │   Forms     │      │                     │      │
│   └─────────────┘      │  • Medications      │      │
│                        │  • Allergies        │      │
│   ┌─────────────┐      │  • Conditions       │      │
│   │   Photo     │─────▶│  • Labs (manual)    │      │
│   │   Upload    │      │  • Emergency Info   │      │
│   │   (OCR)     │      │                     │      │
│   └─────────────┘      └─────────┬───────────┘      │
│                                  │                   │
│                                  ▼                   │
│                        ┌─────────────────────┐      │
│                        │   Share Module      │      │
│                        │                     │      │
│                        │  Generate Link ──────────▶ Doctor View
│                        │  (24hr expiry)      │      │  (Web Page)
│                        │  QR Code            │      │
│                        └─────────────────────┘      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 5 Deliverables

### Week 1: Profile Entry
- [ ] **D1**: Mobile-first form for medications (name, dose, frequency)
- [ ] **D2**: Allergies list with severity indicator
- [ ] **D3**: Conditions/diagnoses list
- [ ] **D4**: Local storage (works offline)

### Week 2: Data Import
- [ ] **D5**: Photo upload for prescriptions/lab reports
- [ ] **D6**: Basic OCR extraction (medication names, lab values)
- [ ] **D7**: Manual correction UI for OCR results

### Week 3: Share Flow
- [ ] **D8**: Generate secure share link (UUID, 24hr expiry)
- [ ] **D9**: QR code generation for in-office sharing
- [ ] **D10**: Doctor view page (read-only summary)
- [ ] **D11**: Access log (who viewed, when)

### Week 4: Polish & Test
- [ ] **D12**: Emergency card (allergies, medications, emergency contact)
- [ ] **D13**: 10-user pilot with real people
- [ ] **D14**: Measure success criteria
- [ ] **D15**: GO/NO-GO decision

---

## What We're NOT Building

| Feature | Why Not |
|---------|---------|
| ❌ Direct EHR integration | Too complex, requires partnerships |
| ❌ FHIR/HL7 import | Enterprise feature, not MVP |
| ❌ Insurance integration | Regulatory complexity |
| ❌ Provider directory | Focus on patient data first |
| ❌ Appointment booking | Different product |
| ❌ Telemedicine | Out of scope |
| ❌ Health tracking/wearables | Feature creep |

---

## Tech Stack (Simple)

```yaml
Frontend:
  - React Native (Expo) or PWA
  - Local SQLite for offline
  - Camera API for photos

Backend:
  - Single Node.js server
  - PostgreSQL (Supabase free tier)
  - Simple REST API

OCR:
  - Google Cloud Vision API (free tier)
  - Or Tesseract.js (client-side, free)

Sharing:
  - UUID-based links
  - No auth required for doctor view
  - 24-hour auto-expiry

Hosting:
  - Vercel (free)
  - Supabase (free tier)
```

**Monthly Cost: $0-20** (free tiers)

---

## User Flows

### Flow 1: Add Medication
```
Open App → "+" Button → "Add Medication"
→ Enter: Name, Dose, Frequency, Prescriber
→ Save → Appears in "My Medications" list
Time: 30 seconds
```

### Flow 2: Photo Import
```
Open App → Camera Icon → Take Photo of Prescription
→ OCR extracts medication name/dose
→ Review/Edit → Confirm → Added to profile
Time: 1 minute
```

### Flow 3: Share with Doctor
```
Open App → "Share" Button → "Generate Link"
→ Copy Link or Show QR → Doctor scans/clicks
→ Doctor sees summary (no login needed)
→ Patient gets notification: "Dr. X viewed your profile"
Time: 30 seconds
```

### Flow 4: Emergency Access
```
Lock Screen Widget → "Emergency Card"
→ Shows: Blood type, Allergies, Medications, Emergency Contact
→ No unlock required
```

---

## Data Model (Minimal)

```sql
-- Patient Profile
patients (
  id, name, dob, blood_type, emergency_contact
)

-- Medications
medications (
  id, patient_id, name, dose, frequency,
  prescriber, start_date, active
)

-- Allergies
allergies (
  id, patient_id, allergen, reaction, severity
)

-- Conditions
conditions (
  id, patient_id, name, diagnosed_date, notes
)

-- Share Links
shares (
  id, patient_id, token, expires_at,
  created_at, accessed_at, accessor_name
)

-- Access Log
access_log (
  id, share_id, accessed_at, ip_address
)
```

---

## GO / NO-GO Decision (Week 4)

### GO ✅ if:
- [ ] 8/10 test users complete profile setup
- [ ] Share flow works in < 2 minutes
- [ ] 5/10 users say "I'd use this for my next doctor visit"
- [ ] Doctor view displays correct information

### NO-GO ❌ if:
- [ ] Users abandon profile setup (too tedious)
- [ ] Share links don't work reliably
- [ ] Users don't trust it with medical data
- [ ] "I'd just bring my paper records"

### Pivot Options if NO-GO:
1. **Simpler**: Emergency-only card (just allergies + meds)
2. **Different angle**: Family health coordinator (manage parents' meds)
3. **B2B**: Sell to clinics as patient intake form

---

## The One Question

> **"Would you use this app before your next doctor's appointment to share your medical info?"**

If 7/10 people say yes → **GO**
If they say "maybe" or "no" → **Pivot or kill**

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| "I don't trust an app with my health data" | Local-first storage, clear privacy policy, no ads ever |
| "Too much work to enter everything" | Start with just medications + allergies (5 min setup) |
| "Doctor won't look at it" | QR code makes it instant, formatted like a standard med list |
| "What if I lose my phone?" | Optional cloud backup (encrypted) |
