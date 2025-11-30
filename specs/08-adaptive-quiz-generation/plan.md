# Implementation Plan: Adaptive Quiz Generation

## Summary

Implement an adaptive quiz system using RMP monad for convergent mastery and comonad for learning context extraction. Integrates with educational datasets for question banks.

---

## Technical Context

| Aspect | Decision |
|--------|----------|
| **Language** | Python 3.11+ |
| **Data** | EdNet, ASSISTments, custom banks |
| **API** | REST for quiz delivery |
| **Frontend** | React (separate repo) |
| **Framework** | Integrates with meta_prompting_engine |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Adaptive Quiz Engine                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Question   │───▶│     RMP      │───▶│   Mastery    │  │
│  │     Bank     │    │    Monad     │    │   Scorer     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Difficulty  │◀──▶│   Comonad    │───▶│  Dashboard   │  │
│  │   Selector   │    │  (Context)   │    │  (Tracking)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown

### Phase 1: Core Types
- Question, Answer, QuizState dataclasses
- LearningContext with history
- Mastery score computation

### Phase 2: RMP Loop
- Monadic quiz iteration
- Early stopping at mastery
- Maximum question limit

### Phase 3: Comonadic Context
- Extract current knowledge
- Extend with new answers
- Track learning trajectory

### Phase 4: Question Selection
- Difficulty-based selection
- Topic coverage balancing
- Prerequisite enforcement

### Phase 5: Dashboard
- Student mastery views
- Teacher analytics
- Progress visualization

---

## Dependencies

```
numpy>=1.24
pandas>=2.0
fastapi>=0.100
```
