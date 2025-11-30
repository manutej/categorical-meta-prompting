# MedX Pro - Prototype Spec

## The Core Bet

> **If a doctor speaks for 3 minutes and gets a SOAP note in 30 seconds, they will adopt this over typing.**

---

## Success Criteria (4 Weeks)

| # | Metric | Target | How to Measure |
|---|--------|--------|----------------|
| 1 | Transcription accuracy | > 90% | Side-by-side comparison with manual transcript |
| 2 | SOAP generation time | < 30 sec | Timer from "stop recording" to "note ready" |
| 3 | Doctor acceptance | 7/10 notes | Doctor clicks "Accept" without major edits |
| 4 | Time saved | > 50% | Compare to typing same note manually |

---

## What We're Building (Only This)

```
┌─────────────────────────────────────────────────────┐
│                    MedX Pro MVP                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│   ┌─────────────┐      ┌─────────────────────┐      │
│   │   Mobile    │      │   Whisper API       │      │
│   │   Record    │─────▶│   (OpenAI)          │      │
│   │   Button    │      │                     │      │
│   └─────────────┘      └──────────┬──────────┘      │
│                                   │                  │
│                                   ▼                  │
│                        ┌─────────────────────┐      │
│                        │   GPT-4 SOAP        │      │
│                        │   Generator         │      │
│                        │   (Single Prompt)   │      │
│                        └──────────┬──────────┘      │
│                                   │                  │
│                                   ▼                  │
│                        ┌─────────────────────┐      │
│                        │   Edit & Accept     │      │
│                        │   Screen            │      │
│                        └─────────────────────┘      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 5 Deliverables

### Week 1-2: Core Recording
- [ ] **D1**: Mobile app with big red "Record" button
- [ ] **D2**: Send audio to Whisper API, get transcript
- [ ] **D3**: Display transcript for review

### Week 3: SOAP Generation
- [ ] **D4**: Single GPT-4 prompt that converts transcript → SOAP note
- [ ] **D5**: Display SOAP with edit capability

### Week 4: Polish & Test
- [ ] **D6**: Test with 3 real doctors (friends/family in medicine)
- [ ] **D7**: Measure success criteria
- [ ] **D8**: GO/NO-GO decision

---

## What We're NOT Building

| Feature | Why Not |
|---------|---------|
| ❌ Custom Whisper fine-tuning | Use OpenAI API first |
| ❌ On-device processing | Cloud is fine for prototype |
| ❌ EHR integration | Manual copy-paste is OK |
| ❌ Voice commands | Just record button |
| ❌ Patient management | Out of scope |
| ❌ Offline mode | Requires connection |
| ❌ Multi-language | Spanish only for now |

---

## Tech Stack (Simple)

```yaml
Mobile: React Native (Expo)
Audio: Expo AV
STT: OpenAI Whisper API
LLM: OpenAI GPT-4 API
Backend: None (direct API calls)
Storage: AsyncStorage (local)
```

**Monthly Cost: ~$50-100** (API usage for testing)

---

## The SOAP Prompt

```
You are a medical scribe. Convert this doctor-patient conversation
into a SOAP note. Use standard medical abbreviations.

Transcript:
{transcript}

Output format:
S (Subjective): [patient's chief complaint, history]
O (Objective): [exam findings, vitals mentioned]
A (Assessment): [likely diagnosis]
P (Plan): [treatment plan, follow-up]
```

---

## GO / NO-GO Decision (Week 4)

### GO ✅ if:
- [ ] 3/3 test doctors say "this saves me time"
- [ ] Transcription accuracy > 90% on Spanish medical speech
- [ ] SOAP notes require < 2 minutes of editing
- [ ] Doctors would pay $50+/month for this

### NO-GO ❌ if:
- [ ] Transcription fails on medical terminology
- [ ] SOAP notes are unusable without major rewrites
- [ ] Doctors say "I'd rather just type"

### Pivot Options if NO-GO:
1. **Narrow focus**: Specific specialty only (dermatology, psychiatry)
2. **Simpler output**: Just transcript, no SOAP
3. **Different market**: Medical students for study notes

---

## The One Question

After each test session, ask the doctor:

> **"Would you use this tomorrow with your real patients?"**

If 2/3 say yes → **GO**
If they hesitate → **Dig deeper on why**
