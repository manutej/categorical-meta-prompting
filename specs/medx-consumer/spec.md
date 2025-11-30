# MedX Consumer - Universal Medical Profile Platform

## Product Vision

**Tagline**: "Your Health. Your Data. Your Control."

MedX Consumer empowers patients with a Universal Medical Profile (UMP) - a portable, patient-owned health record that travels with them across any provider, lab, or pharmacy. Patients control who sees their data and can share it with a tap.

## Problem Statement

Patients have no control over their medical data:
- Records scattered across providers, labs, pharmacies
- Repeat tests because results don't travel
- No visibility into who accesses their information
- Switching providers means starting from scratch
- Emergency situations lack critical medical history

## Target Users

- **Primary**: Patients/Healthcare consumers
- **Secondary**: Caregivers (for dependents, elderly)
- **Tertiary**: Employers (voluntary wellness programs)

## Categorical Structure

### Colimit: Data Aggregation
```
colim: {Provider₁, Lab₁, Pharmacy₁, ...} → UniversalMedicalProfile

Objects: Disparate health records from multiple sources
Cocone: Unified patient view reconciling all sources
Universal property: Any view factors through UMP
```

### Comonad: Context-Aware Sharing
```
W: FullProfile → SharedContext

extract: Full profile → Relevant subset for context
extend: Local sharing → Global consent management
duplicate: Sharing context → Meta-sharing (who can see who saw)
```

### Enriched Category: Consent & Privacy
```
Q: [0,1]^3 privacy dimensions
- Granularity: How specific the sharing (all vs subset)
- Duration: Time-bounded vs permanent access
- Purpose: General vs specific use authorization
```

### Functor: Profile Transformation
```
F: InternalProfile → SharedView

Different functors for different sharing contexts:
- F_emergency: Critical info only (allergies, conditions, meds)
- F_specialist: Relevant history for specialty
- F_research: De-identified for studies
```

---

## User Stories

### Epic 1: Universal Medical Profile (UMP)

#### US-1.1: Profile Creation [P1]
**As a** new user
**I want** to create my Universal Medical Profile
**So that** I have a single place for all my health data

**Acceptance Criteria:**
- [ ] Sign up with email/phone/social
- [ ] Identity verification (government ID + selfie)
- [ ] Basic demographics capture
- [ ] Emergency contact setup
- [ ] Initial health questionnaire (optional)
- [ ] Profile completeness indicator

#### US-1.2: Data Import [P1]
**As a** user with existing health records
**I want** to import my data from providers
**So that** my UMP is comprehensive

**Acceptance Criteria:**
- [ ] Connect via MedX Pro (providers in network)
- [ ] FHIR patient access (Blue Button 2.0)
- [ ] Manual upload (PDF, images)
- [ ] Lab result import (MedX Connect)
- [ ] Pharmacy history import
- [ ] Wearable device sync (Apple Health, Google Fit)

#### US-1.3: Profile Dashboard [P1]
**As a** user
**I want** to see my complete health picture
**So that** I understand my health status

**Acceptance Criteria:**
- [ ] Active conditions summary
- [ ] Current medications with refill status
- [ ] Recent lab results with trends
- [ ] Upcoming appointments
- [ ] Immunization records
- [ ] Allergies prominently displayed
- [ ] Care team list

#### US-1.4: Health Timeline [P2]
**As a** user
**I want** to see my health history chronologically
**So that** I can track my health journey

**Acceptance Criteria:**
- [ ] Chronological event view
- [ ] Filter by type (visits, labs, procedures)
- [ ] Search within timeline
- [ ] Event detail expansion
- [ ] Export timeline as PDF/FHIR

### Epic 2: Data Ownership & Consent

#### US-2.1: Consent Management [P1]
**As a** user
**I want** to control who can access my data
**So that** my privacy is protected

**Acceptance Criteria:**
- [ ] View all active consents
- [ ] Grant consent to provider (via code/QR)
- [ ] Revoke consent at any time
- [ ] Set consent expiration
- [ ] Specify data scope (all vs categories)
- [ ] Consent history audit log

#### US-2.2: Granular Sharing [P1]
**As a** user sharing with a specialist
**I want** to share only relevant information
**So that** I maintain privacy for unrelated conditions

**Acceptance Criteria:**
- [ ] Select specific sections to share
- [ ] Date range filtering
- [ ] Condition-specific sharing
- [ ] Exclude sensitive categories (mental health, HIV)
- [ ] Preview what will be shared
- [ ] Share summary vs full detail

#### US-2.3: Access Log [P1]
**As a** user
**I want** to see who accessed my data
**So that** I can verify proper use

**Acceptance Criteria:**
- [ ] Real-time access notifications (optional)
- [ ] Access log with timestamp, entity, data accessed
- [ ] Flag suspicious access
- [ ] Export access log
- [ ] Report unauthorized access

#### US-2.4: Emergency Access [P1]
**As a** user with medical emergency
**I want** first responders to access critical info
**So that** I receive appropriate emergency care

**Acceptance Criteria:**
- [ ] Emergency profile subset (allergies, meds, conditions)
- [ ] Emergency QR code (wallet, lock screen)
- [ ] Break-the-glass access for verified EMTs
- [ ] Emergency access logged and notified
- [ ] ICE contact notification

### Epic 3: Provider Interaction

#### US-3.1: Provider Search & Booking [P2]
**As a** user seeking care
**I want** to find and book providers
**So that** I can access healthcare conveniently

**Acceptance Criteria:**
- [ ] Search by specialty, location, insurance
- [ ] View availability in real-time
- [ ] Book appointment directly
- [ ] Reschedule/cancel appointments
- [ ] Appointment reminders
- [ ] Provider ratings and reviews

#### US-3.2: Pre-Visit Profile Sharing [P1]
**As a** user with upcoming appointment
**I want** to share my profile before the visit
**So that** the provider is prepared

**Acceptance Criteria:**
- [ ] Pre-visit consent request from provider
- [ ] One-tap approval with recommended scope
- [ ] Custom scope adjustment
- [ ] Confirmation of successful share
- [ ] Post-visit consent auto-revocation option

#### US-3.3: Visit Summary Receipt [P2]
**As a** user after a provider visit
**I want** to receive the visit summary
**So that** my UMP stays updated

**Acceptance Criteria:**
- [ ] Automatic import from MedX Pro providers
- [ ] New conditions, medications added
- [ ] Visit notes in timeline
- [ ] Follow-up tasks visible
- [ ] Prescription sent to pharmacy visible

### Epic 4: Medication Management

#### US-4.1: Medication List [P1]
**As a** user
**I want** to see all my medications
**So that** I manage my treatment effectively

**Acceptance Criteria:**
- [ ] Active medications with dosage
- [ ] Prescribing provider
- [ ] Pharmacy where filled
- [ ] Refills remaining
- [ ] Discontinued medications history

#### US-4.2: Medication Reminders [P2]
**As a** user on multiple medications
**I want** reminders to take my medications
**So that** I maintain adherence

**Acceptance Criteria:**
- [ ] Configurable reminder schedules
- [ ] Confirm/snooze/skip actions
- [ ] Adherence tracking
- [ ] Refill reminders before running out
- [ ] Caregiver notification for missed doses

#### US-4.3: Interaction Alerts [P1]
**As a** user
**I want** to be warned about drug interactions
**So that** I avoid dangerous combinations

**Acceptance Criteria:**
- [ ] Alert when new prescription has interaction
- [ ] Explain severity and effects
- [ ] Prompt to discuss with prescriber
- [ ] OTC medication checker
- [ ] Food/supplement interaction info

### Epic 5: Lab Results & Health Data

#### US-5.1: Lab Result Viewing [P1]
**As a** user
**I want** to view my lab results
**So that** I understand my health metrics

**Acceptance Criteria:**
- [ ] Results organized by date and type
- [ ] Normal range indicators
- [ ] Abnormal values highlighted
- [ ] Trend charts over time
- [ ] Plain-language explanations
- [ ] Reference information links

#### US-5.2: Result Sharing with Providers [P1]
**As a** user seeing a new doctor
**I want** to share my lab history
**So that** they have baseline data

**Acceptance Criteria:**
- [ ] Select specific results to share
- [ ] Share via consent code
- [ ] Provider receives in their workflow (MedX Pro)
- [ ] Confirmation of receipt
- [ ] Shared results logged

#### US-5.3: Wearable Integration [P3]
**As a** user with health wearables
**I want** to include that data in my profile
**So that** I have a complete picture

**Acceptance Criteria:**
- [ ] Apple Health integration
- [ ] Google Fit integration
- [ ] Blood pressure monitors
- [ ] Glucose monitors
- [ ] Sleep trackers
- [ ] Data visible in UMP timeline

### Epic 6: Family & Caregivers

#### US-6.1: Dependent Profiles [P2]
**As a** parent
**I want** to manage my children's profiles
**So that** I coordinate their healthcare

**Acceptance Criteria:**
- [ ] Create dependent profile
- [ ] Full access until age 13
- [ ] Graduated access 13-18
- [ ] Transfer ownership at 18
- [ ] Shared appointments view
- [ ] Vaccination tracking

#### US-6.2: Caregiver Access [P2]
**As an** elderly patient
**I want** to grant my adult child access
**So that** they can help manage my care

**Acceptance Criteria:**
- [ ] Designate caregiver with access level
- [ ] View-only vs manage permissions
- [ ] Appointment management delegation
- [ ] Caregiver notifications
- [ ] Revoke caregiver access anytime

#### US-6.3: Family Health History [P3]
**As a** user
**I want** to record family health history
**So that** providers understand my risk factors

**Acceptance Criteria:**
- [ ] Add family members and relationships
- [ ] Record conditions by family member
- [ ] Generate family health tree
- [ ] Risk factor analysis
- [ ] Share with providers for screening recommendations

---

## Non-Functional Requirements

### Performance
- App launch: < 2 seconds
- Profile load: < 1 second
- Consent grant: < 500ms
- Search results: < 1 second

### Security
- End-to-end encryption for all health data
- Biometric authentication (Face ID, fingerprint)
- PIN fallback
- Device binding
- Remote wipe capability
- No data stored unencrypted on device

### Privacy
- HIPAA compliant
- GDPR compliant (for EU markets)
- Data minimization in sharing
- Right to erasure ("delete my data")
- Data portability (FHIR export)

### Accessibility
- WCAG 2.1 AA compliance
- VoiceOver/TalkBack support
- Large text support
- High contrast mode
- Reduced motion option

### Availability
- 99.9% uptime
- Offline access to cached profile
- Graceful degradation

---

## Data Model

### Core Entities

```
UniversalMedicalProfile {
  id: UUID (UMP ID - portable identifier)
  user_id: UUID
  demographics: Demographics
  emergency_contacts: EmergencyContact[]
  insurance: Insurance[]
  care_team: CareTeamMember[]

  // Clinical data (Colimit of all sources)
  conditions: Condition[]
  medications: Medication[]
  allergies: Allergy[]
  immunizations: Immunization[]
  procedures: Procedure[]
  lab_results: LabResult[]
  encounters: Encounter[]
  documents: Document[]

  // Consent management
  active_consents: Consent[]
  access_log: AccessLogEntry[]

  // Metadata
  completeness_score: float
  last_updated: Timestamp
  data_sources: DataSource[]
}

Consent {
  id: UUID
  grantor: UUID (patient)
  grantee: EntityReference (provider, org)
  scope: ConsentScope
  granted_at: Timestamp
  expires_at: Timestamp (optional)
  status: ConsentStatus
  purpose: ConsentPurpose

  // Enriched privacy dimensions
  privacy_vector: PrivacyVector
}

ConsentScope {
  type: ScopeType (full, category, specific)
  categories: Category[] (if category-based)
  date_range: DateRange (optional)
  exclude: Category[] (sensitive exclusions)
}

PrivacyVector {
  granularity: float [0,1]  // 0=all, 1=specific items only
  duration: float [0,1]     // 0=permanent, 1=one-time
  purpose_limitation: float [0,1]  // 0=general, 1=specific purpose

  aggregate(): float  // Overall restrictiveness
}

AccessLogEntry {
  timestamp: Timestamp
  accessor: EntityReference
  data_accessed: DataCategory[]
  purpose: AccessPurpose
  consent_id: UUID
  ip_address: string (hashed)
  flagged: boolean
}

DataSource {
  type: SourceType (provider, lab, pharmacy, patient, wearable)
  entity_id: UUID (optional)
  connected_at: Timestamp
  last_sync: Timestamp
  status: SyncStatus
}
```

---

## API Contracts

### Profile API

```
GET /v1/profile
Authorization: Bearer {user_token}

Response:
{
  "ump_id": "uuid",
  "demographics": {...},
  "conditions": [...],
  "medications": [...],
  "allergies": [...],
  "completeness_score": 0.85,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Consent API

```
POST /v1/consent/grant
{
  "grantee": {
    "type": "provider",
    "id": "provider-uuid"
  },
  "scope": {
    "type": "category",
    "categories": ["medications", "allergies", "lab_results"],
    "exclude": ["mental_health"]
  },
  "expires_in_days": 30,
  "purpose": "specialist_consultation"
}

Response:
{
  "consent_id": "uuid",
  "share_code": "ABC123",  // For provider to claim
  "qr_code_url": "https://...",
  "expires_at": "2024-02-15T10:30:00Z"
}
```

### Provider Sharing API

```
POST /v1/share/provider
{
  "provider_code": "DRJONES",
  "scope": "recommended",  // or "custom"
  "custom_scope": {...}    // if custom
}

Response:
{
  "share_id": "uuid",
  "status": "pending_acceptance",
  "provider": {
    "name": "Dr. Maria Jones",
    "specialty": "Cardiology"
  },
  "data_preview": {
    "conditions_count": 3,
    "medications_count": 5,
    "lab_results_count": 12
  }
}
```

### Emergency Access API

```
GET /v1/emergency/{emergency_token}
Authorization: Bearer {emt_credential}

Response:
{
  "patient_name": "Juan Pérez",
  "allergies": [
    {"substance": "Penicillin", "severity": "severe"}
  ],
  "conditions": [
    {"name": "Type 2 Diabetes", "status": "active"},
    {"name": "Hypertension", "status": "controlled"}
  ],
  "medications": [
    {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
    {"name": "Lisinopril", "dosage": "10mg", "frequency": "daily"}
  ],
  "emergency_contacts": [...],
  "blood_type": "O+",
  "advance_directives": "Full code"
}
```

---

## Success Metrics

### Adoption
- Registered users: 1M in Year 1
- Monthly active users: 40% of registered
- Profile completeness average: > 60%

### Engagement
- Data imports per user: > 3 sources
- Consents granted per user/year: > 5
- App opens per month: > 4

### Value
- Users who avoided repeat test: 30%
- Emergency access uses: Track count
- Provider satisfaction with shared data: > 4.0/5.0

### Trust
- Consent revocations: < 10%
- Reported unauthorized access: < 0.1%
- Data deletion requests: < 5%

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Data breach | Critical | Low | Encryption, security audits, insurance |
| Low adoption | High | Medium | Free tier, provider incentives, easy onboarding |
| Incomplete data | Medium | High | Gamification, import wizards, provider encouragement |
| Provider non-participation | High | Medium | MedX Pro integration, network effects |
| Regulatory changes | Medium | Medium | Compliance monitoring, adaptable architecture |

---

## Dependencies

- **MedX Pro**: Provider data source, consent recipient
- **MedX Connect**: Lab results, pharmacy data
- **External**: Identity verification service, FHIR endpoints (Blue Button)

---

## Glossary

- **UMP**: Universal Medical Profile - the portable patient health record
- **Consent**: Patient authorization for data access
- **Colimit**: Categorical construction unifying multiple data sources
- **Break-the-glass**: Emergency access overriding normal consent
- **ICE**: In Case of Emergency (contact)
- **Blue Button**: CMS initiative for patient data access (FHIR-based)
