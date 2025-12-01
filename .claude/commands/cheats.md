---
description: Quick help on generated cheat sheets with depth tree search across files
allowed-tools: Read, Glob, Grep
argument-hint: [topic] or --list or --full
---

# Categorical Meta-Prompting Cheat Sheet Quick Reference

Display quick reference help for categorical meta-prompting commands, syntax, and patterns.

## Arguments

- No argument: Show condensed quick reference
- `--list`: List all available sections
- `--full`: Display the complete cheat sheet
- `[topic]`: Search for specific topic (e.g., "functor", "monad", "quality", "chain")

## Request: $ARGUMENTS

---

## Execution

Based on the arguments provided, display the appropriate help:

### If no argument or condensed help requested:

Display this condensed quick reference:

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║            CATEGORICAL META-PROMPTING v2.2 - QUICK REFERENCE                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  THE FOUR PILLARS                                                             ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  FUNCTOR F          MONAD M           COMONAD W         NAT. TRANS. α        ║
║  Task → Prompt      Prompt →ⁿ Prompt  History → Context F ⇒ G                ║
║  /meta              /rmp              /context          /transform           ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  QUICK COMMANDS                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  /meta "task"                    Basic transformation                         ║
║  /meta @domain:SECURITY "task"   Domain-specific                              ║
║  /rmp @quality:0.85 "task"       Quality-gated iteration                      ║
║  /context @mode:extract "task"   Extract context                              ║
║  /transform @to:cot "task"       Switch strategy                              ║
║  /chain [/a → /b] "task"         Sequential composition                       ║
║  /chain [/a || /b] "task"        Parallel execution                           ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  COMPOSITION OPERATORS                                                        ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  →    Sequential    Output A → Input B           min(q₁, q₂)                  ║
║  ||   Parallel      Run concurrently             mean(q₁, q₂, ...)            ║
║  ⊗    Tensor        Combine structures           min(q₁, q₂)                  ║
║  >=>  Kleisli       Quality-gated chain          improves iteratively         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  MODIFIERS                                                                    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  @mode:       active, iterative, dry-run, spec                                ║
║  @quality:    0.0-1.0 (threshold)                                             ║
║  @tier:       L1-L7 (complexity)                                              ║
║  @domain:     ALGORITHM, SECURITY, API, DEBUG, TESTING                        ║
║  @template:   {context}+{mode}+{format}                                       ║
║  @focus:      recent, all, file, conversation                                 ║
║  @depth:      1-10                                                            ║
║  @from:/@to:  zero-shot, few-shot, chain-of-thought, tree-of-thought         ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  QUALITY THRESHOLDS                                                           ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  ≥0.90  Excellent    0.80-0.90  Good    0.70-0.80  OK                        ║
║  0.60-0.70  Poor     <0.60  Failed                                           ║
║                                                                               ║
║  q = 0.40×correctness + 0.25×clarity + 0.20×completeness + 0.15×efficiency   ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  COMMON RECIPES                                                               ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                               ║
║  Quick fix:     /meta "fix bug"                                               ║
║  Quality impl:  /rmp @quality:0.85 "implement feature"                        ║
║  Context-aware: /chain [/context → /meta] "task"                              ║
║  Code review:   /meta-review "file.ts"                                        ║
║  Debug:         /chain [/context → /debug → /meta @domain:DEBUG] "error"      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Use /cheats --full for complete cheat sheet
Use /cheats [topic] to search for specific topic
```

### If `--list` requested:

List all available sections from the cheat sheet:
- Core Categorical Structures (The Four Pillars)
- Quick Command Reference (Functor, Monad, Comonad, Natural Transformation)
- Composition Operators (→, ||, ⊗, >=>)
- Modifiers Quick Reference
- Tier Classification (L1-L7)
- Quality Assessment
- Common Workflows
- Template Components
- Strategy Registry
- Categorical Laws
- Checkpoint Format
- Quick Recipes
- Troubleshooting
- File Locations

### If `--full` requested:

Read and display the complete cheat sheet from:
`/Users/manu/Documents/LUXOR/categorical-meta-prompting/docs/CHEAT-SHEET.md`

### If `[topic]` provided:

Search for the topic in the cheat sheet and display relevant sections. Common topics:
- functor, monad, comonad, transform (structures)
- chain, compose, sequence, parallel (composition)
- quality, threshold, assessment (quality)
- tier, L1-L7, complexity (tiers)
- modifier, mode, domain (syntax)
- workflow, recipe, pipeline (patterns)
- law, identity, associativity (theory)

---

## Available Files

- **Light theme**: `docs/CHEAT-SHEET.md`
- **Dark theme (terminal)**: `docs/CHEAT-SHEET-DARK.md`
- **PDF (light)**: `docs/light/CHEAT-SHEET-light.pdf`
- **PDF (dark)**: `docs/dark/CHEAT-SHEET-dark.pdf`

---

## Tips

1. Use `/cheats` for quick reference during development
2. Use `/cheats --full` to see all details
3. Use `/cheats quality` to find quality assessment info
4. Use `/cheats chain` to see composition examples
5. Print the PDF for offline reference
