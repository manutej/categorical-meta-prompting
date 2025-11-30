# MedX Consumer - Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     MedX Consumer Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Mobile Applications                           │   │
│  │   ┌───────────┐              ┌───────────┐                      │   │
│  │   │    iOS    │              │  Android  │                      │   │
│  │   │   App     │              │   App     │                      │   │
│  │   └─────┬─────┘              └─────┬─────┘                      │   │
│  │         │    React Native Core     │                            │   │
│  │         └───────────┬──────────────┘                            │   │
│  └─────────────────────┼───────────────────────────────────────────┘   │
│                        │                                                │
│                        ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      API Gateway                                 │   │
│  │           (Auth, Rate Limiting, Request Routing)                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                │
│        ┌───────────────┼───────────────┬───────────────┐               │
│        ▼               ▼               ▼               ▼               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │  Profile  │  │  Consent  │  │   Data    │  │  Sharing  │          │
│  │  Service  │  │  Service  │  │  Import   │  │  Service  │          │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘          │
│        │               │               │               │               │
│        └───────────────┴───────────────┴───────────────┘               │
│                        │                                                │
│                        ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   UMP Data Layer (Colimit)                       │   │
│  │  ┌────────────────────────────────────────────────────────┐     │   │
│  │  │              Profile Aggregation Engine                 │     │   │
│  │  │   Unifies data from: Providers, Labs, Pharmacies,      │     │   │
│  │  │   Patient input, Wearables → Single coherent UMP       │     │   │
│  │  └────────────────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                │
│                        ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Data Storage Layer                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                 │   │
│  │  │ PostgreSQL │  │   Redis    │  │ S3/Blob    │                 │   │
│  │  │ (Profiles, │  │  (Cache,   │  │(Documents, │                 │   │
│  │  │  Consents) │  │  Sessions) │  │ Images)    │                 │   │
│  │  └────────────┘  └────────────┘  └────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                │
│        ┌───────────────┴───────────────┬───────────────┐               │
│        ▼                               ▼               ▼               │
│  ┌───────────────┐            ┌───────────────┐ ┌───────────────┐     │
│  │  MedX Connect │            │   MedX Pro    │ │ External FHIR │     │
│  │  (Labs, Rx)   │            │  (Providers)  │ │ (Blue Button) │     │
│  └───────────────┘            └───────────────┘ └───────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Technical Decisions

### TD-1: Mobile Framework
**Decision**: React Native with native modules for sensitive operations
**Rationale**:
- Single codebase for iOS and Android
- Native modules for biometrics, secure storage
- Large ecosystem and talent pool
- Good performance for data-centric apps
**Trade-offs**: Some performance overhead vs pure native

### TD-2: Profile Storage Architecture
**Decision**: Colimit-based aggregation with source tracking
**Rationale**:
- Categorical colimit naturally unifies multiple data sources
- Source tracking enables provenance and updates
- Conflict resolution at aggregation time
- Supports incremental sync
**Categorical Mapping**: Colimit in Category of Health Records

### TD-3: Consent Model
**Decision**: Comonad-based context-aware consent
**Rationale**:
- extract: Get minimal data for context
- extend: Apply consent rules globally
- Composable consent operations
- Supports complex sharing scenarios
**Categorical Mapping**: Comonad W: Profile → SharedContext

### TD-4: Encryption Strategy
**Decision**: Client-side encryption with key hierarchy
**Rationale**:
- Data encrypted before leaving device
- Server never sees plaintext PHI
- Key derived from user credential
- Recovery via secure key escrow
**Trade-offs**: Search/query limitations, key management complexity

### TD-5: Offline Support
**Decision**: Encrypted local cache with sync on connect
**Rationale**:
- Healthcare access critical in low-connectivity areas
- Emergency access must work offline
- Sync conflicts resolved by timestamp + source priority
**Trade-offs**: Cache invalidation complexity, storage limits

### TD-6: Identity Verification
**Decision**: Third-party KYC + healthcare credential linking
**Rationale**:
- Government ID verification for trust
- Link to existing health system IDs
- Prevents fraudulent profile creation
- Enables inter-system matching
**Trade-offs**: Onboarding friction, vendor dependency

---

## Phase Breakdown

### Phase 1: Core Profile & Auth (Weeks 1-8)

**Objectives:**
- User registration and authentication
- Basic profile creation
- Identity verification integration

**Deliverables:**
- [ ] React Native app scaffolding
- [ ] Authentication service (email, phone, social)
- [ ] Biometric auth (Face ID, fingerprint)
- [ ] Identity verification integration
- [ ] Basic profile data model
- [ ] Secure storage implementation

**Quality Gate:** User can create verified account, basic profile working

### Phase 2: Data Import & Aggregation (Weeks 9-16)

**Objectives:**
- MedX ecosystem data import
- External FHIR import
- Manual data entry
- Colimit aggregation

**Deliverables:**
- [ ] MedX Connect integration (labs, pharmacy)
- [ ] MedX Pro integration (provider records)
- [ ] Blue Button FHIR import
- [ ] Manual entry forms
- [ ] Document upload (PDF, images)
- [ ] Colimit aggregation engine
- [ ] Conflict resolution logic

**Quality Gate:** Complete profile from 3+ sources, no duplicate data

### Phase 3: Consent & Sharing (Weeks 17-24)

**Objectives:**
- Consent management system
- Provider sharing workflow
- Access logging
- Emergency access

**Deliverables:**
- [ ] Consent service with Comonad pattern
- [ ] QR code / share code generation
- [ ] Provider consent claim workflow
- [ ] Granular scope selection UI
- [ ] Access log with notifications
- [ ] Emergency profile and QR
- [ ] Break-the-glass emergency access

**Quality Gate:** Full consent lifecycle working, emergency access functional

### Phase 4: Provider Interaction (Weeks 25-30)

**Objectives:**
- Provider discovery
- Appointment booking
- Pre-visit sharing
- Post-visit import

**Deliverables:**
- [ ] Provider search (via MedX Connect)
- [ ] Appointment booking integration
- [ ] Pre-visit consent workflow
- [ ] Post-visit data import trigger
- [ ] Care team management
- [ ] Provider messaging (basic)

**Quality Gate:** End-to-end provider visit flow working

### Phase 5: Medication & Health Tracking (Weeks 31-36)

**Objectives:**
- Medication management
- Adherence tracking
- Interaction alerts
- Wearable integration

**Deliverables:**
- [ ] Medication list management
- [ ] Reminder system
- [ ] Adherence tracking
- [ ] Drug interaction alerts (via MedX Connect)
- [ ] Apple Health integration
- [ ] Google Fit integration
- [ ] Health trends visualization

**Quality Gate:** Medication reminders working, wearables syncing

### Phase 6: Family & Caregivers (Weeks 37-42)

**Objectives:**
- Dependent profiles
- Caregiver access
- Family health history

**Deliverables:**
- [ ] Dependent profile creation
- [ ] Age-based access controls
- [ ] Caregiver invitation/management
- [ ] Family health history module
- [ ] Multi-profile switching
- [ ] Caregiver notifications

**Quality Gate:** Parent managing child profile, caregiver access working

### Phase 7: Polish & Accessibility (Weeks 43-46)

**Objectives:**
- Accessibility compliance
- Performance optimization
- UX refinement

**Deliverables:**
- [ ] WCAG 2.1 AA audit and fixes
- [ ] Performance profiling and optimization
- [ ] Animation and polish
- [ ] Localization (Spanish, English)
- [ ] Onboarding tutorial
- [ ] Help and FAQ

**Quality Gate:** Accessibility audit passed, app store ready

### Phase 8: Security & Launch (Weeks 47-52)

**Objectives:**
- Security audit
- Compliance verification
- App store submission
- Launch

**Deliverables:**
- [ ] Penetration testing
- [ ] HIPAA compliance documentation
- [ ] Privacy policy and terms
- [ ] App store submission (iOS, Android)
- [ ] Launch marketing
- [ ] Support system setup

**Quality Gate:** Security audit passed, apps approved and live

---

## Categorical Implementation Patterns

### Colimit: Profile Aggregation

```python
class ProfileColimit:
    """
    colim: {Source₁, Source₂, ...} → UniversalMedicalProfile

    Unifies health data from multiple sources into single coherent profile.
    """

    def aggregate(self, sources: List[DataSource]) -> UniversalMedicalProfile:
        """Compute colimit of all source data"""
        # Cocone: Each source maps to unified profile
        cocone_legs = [self.source_to_profile(s) for s in sources]

        # Universal property: Factor through single UMP
        ump = UniversalMedicalProfile()

        for leg in cocone_legs:
            ump = self.merge(ump, leg)

        return ump

    def merge(self, ump: UMP, new_data: PartialProfile) -> UMP:
        """Merge new data respecting colimit structure"""
        for condition in new_data.conditions:
            existing = self.find_matching(ump.conditions, condition)
            if existing:
                ump.conditions.update(existing, self.reconcile(existing, condition))
            else:
                ump.conditions.add(condition)
        # Similar for medications, allergies, etc.
        return ump

    def reconcile(self, existing: ClinicalEntity, new: ClinicalEntity) -> ClinicalEntity:
        """Resolve conflicts between sources"""
        # Prefer more recent, higher-trust source
        if new.source.trust > existing.source.trust:
            return new.with_provenance(existing)
        return existing.with_cross_reference(new)
```

### Comonad: Context-Aware Sharing

```python
class SharingComonad:
    """
    W: FullProfile → SharedContext

    Comonad for context-aware data sharing with consent management.
    """

    def extract(self, profile: FullProfile, context: SharingContext) -> SharedData:
        """
        Extract relevant subset for sharing context.
        Core comonad operation: W A → A
        """
        consent = context.consent
        functor = self.get_sharing_functor(context.purpose)

        # Apply consent scope filtering
        filtered = self.apply_scope(profile, consent.scope)

        # Transform to appropriate view
        return functor.map(filtered)

    def extend(self, profile: FullProfile,
               f: Callable[[FullProfile], SharedData]) -> ConsentAwareProfile:
        """
        Extend local sharing to global consent management.
        W A → W (W A → B) → W B
        """
        return ConsentAwareProfile(
            data=profile,
            sharing_at=lambda ctx: f(profile.focused_on(ctx))
        )

    def duplicate(self, profile: FullProfile) -> AuditableProfile:
        """
        W A → W W A
        Creates meta-level: who can see who has seen
        """
        return AuditableProfile(
            data=profile,
            access_log=profile.access_log,
            sharing_of_log=self.extract  # Can share the access log itself
        )
```

### Privacy-Enriched Consent

```python
class PrivacyEnrichedConsent:
    """
    Consent with [0,1]^3 privacy dimensions.
    Composition degrades privacy (more exposure).
    """

    def compose(self, c1: Consent, c2: Consent) -> Consent:
        """Composition of consents (e.g., re-sharing)"""
        return Consent(
            scope=self.intersect_scope(c1.scope, c2.scope),
            privacy=PrivacyVector(
                # Re-sharing reduces granularity
                granularity=min(c1.privacy.granularity, c2.privacy.granularity),
                # Duration limited by shortest
                duration=max(c1.privacy.duration, c2.privacy.duration),
                # Purpose must be at least as specific
                purpose_limitation=max(
                    c1.privacy.purpose_limitation,
                    c2.privacy.purpose_limitation
                )
            )
        )

    def meets_threshold(self, consent: Consent, required: PrivacyVector) -> bool:
        """Check if consent meets privacy requirements"""
        return (
            consent.privacy.granularity >= required.granularity and
            consent.privacy.duration >= required.duration and
            consent.privacy.purpose_limitation >= required.purpose_limitation
        )
```

### Profile Transformation Functors

```python
class EmergencyFunctor:
    """F_emergency: Profile → EmergencyView"""

    def map(self, profile: FullProfile) -> EmergencyView:
        """Extract only critical emergency information"""
        return EmergencyView(
            allergies=profile.allergies,  # All allergies critical
            conditions=[c for c in profile.conditions if c.is_active],
            medications=[m for m in profile.medications if m.is_current],
            blood_type=profile.blood_type,
            emergency_contacts=profile.emergency_contacts[:3],
            advance_directives=profile.advance_directives
        )


class SpecialistFunctor:
    """F_specialist: Profile → SpecialtyView"""

    def __init__(self, specialty: Specialty):
        self.specialty = specialty

    def map(self, profile: FullProfile) -> SpecialtyView:
        """Extract relevant data for specialty"""
        relevant_conditions = [
            c for c in profile.conditions
            if self.is_relevant(c, self.specialty)
        ]
        return SpecialtyView(
            conditions=relevant_conditions,
            medications=self.relevant_medications(profile, relevant_conditions),
            lab_results=self.relevant_labs(profile, self.specialty),
            procedures=self.relevant_procedures(profile, self.specialty)
        )


class ResearchFunctor:
    """F_research: Profile → DeidentifiedData"""

    def map(self, profile: FullProfile) -> DeidentifiedData:
        """De-identify for research use"""
        return DeidentifiedData(
            demographics=self.generalize_demographics(profile.demographics),
            conditions=[self.deidentify(c) for c in profile.conditions],
            medications=[self.deidentify(m) for m in profile.medications],
            # No dates, locations, or identifiers
        )
```

---

## Data Flow Diagrams

### Profile Creation Flow

```
User                    App                     Backend                 External
  │                      │                         │                       │
  │  Sign up             │                         │                       │
  ├─────────────────────►│                         │                       │
  │                      │  Create account         │                       │
  │                      ├────────────────────────►│                       │
  │                      │                         │  ID verification      │
  │                      │                         ├──────────────────────►│
  │                      │                         │  Verified             │
  │  Upload ID + Selfie  │                         │◄──────────────────────┤
  ├─────────────────────►│                         │                       │
  │                      │  Verify identity        │                       │
  │                      ├────────────────────────►│                       │
  │  Enter demographics  │                         │                       │
  ├─────────────────────►│                         │                       │
  │                      │  Create UMP             │                       │
  │                      ├────────────────────────►│                       │
  │  Profile created     │                         │                       │
  │◄─────────────────────┤                         │                       │
```

### Consent & Sharing Flow

```
Patient                Provider (MedX Pro)        MedX Consumer Backend
   │                         │                            │
   │                         │  Request patient data      │
   │                         ├───────────────────────────►│
   │  Consent request        │                            │
   │◄────────────────────────┼────────────────────────────┤
   │                         │                            │
   │  Review scope           │                            │
   │  Grant consent          │                            │
   ├─────────────────────────┼───────────────────────────►│
   │                         │                            │
   │                         │                            │ Apply Comonad
   │                         │                            │ extract()
   │                         │  Shared data (filtered)    │
   │                         │◄───────────────────────────┤
   │  Access logged          │                            │
   │◄────────────────────────┼────────────────────────────┤
```

---

## Team Structure

```
MedX Consumer Team
├── Mobile Team (5)
│   ├── Mobile Lead (React Native)
│   ├── iOS Native Specialist
│   ├── Android Native Specialist
│   ├── Mobile Engineers (2)
├── Backend Team (4)
│   ├── Backend Lead
│   ├── Backend Engineers (2)
│   └── Security Engineer
├── Data Team (2)
│   ├── Data Engineer (FHIR/Integration)
│   └── ML Engineer (Matching/Dedup)
├── Design Team (2)
│   ├── UX Designer
│   └── UX Researcher
└── Product (2)
    ├── Product Manager
    └── Compliance/Privacy Officer
```

---

## Success Criteria

| Milestone | Criteria | Target |
|-----------|----------|--------|
| Alpha | Profile creation working | Week 8 |
| Beta | Multi-source import | Week 16 |
| RC | Full consent lifecycle | Week 24 |
| GA | App store launch | Week 52 |
| Scale | 1M users | Year 1 |
