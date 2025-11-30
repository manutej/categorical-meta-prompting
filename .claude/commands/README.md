# Meta-Prompting Slash Commands

**Core insight**: Slash commands ARE prompts. Commands calling commands = prompts calling prompts.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  META-PROMPT LAYER (prompts that call other prompts)        │
│                                                             │
│  /route     → Analyze task, route to appropriate command    │
│  /chain     → Execute: /cmd1 → /cmd2 → /cmd3                │
│  /meta      → Strategy selection + domain routing           │
│  /build-prompt → Assemble template from components          │
│  /template  → Build prompt step-by-step, visible states     │
└─────────────────────────────────────────────────────────────┘
                          ↓ calls
┌─────────────────────────────────────────────────────────────┐
│  OBJECT-PROMPT LAYER (prompts that do work)                 │
│                                                             │
│  /debug     → Reproduce → Isolate → Hypothesize → Fix       │
│  /review    → Classify domain → Apply focused review        │
│  /compose   → {prompt:analyze} → {prompt:plan} → ...        │
│  /rmp       → Execute → Assess → Refine → Repeat            │
└─────────────────────────────────────────────────────────────┘
                          ↓ uses
┌─────────────────────────────────────────────────────────────┐
│  TEMPLATE COMPONENTS (embedded, dynamically selected)       │
│                                                             │
│  {context:expert}  {context:teacher}  {context:debugger}    │
│  {mode:direct}     {mode:cot}         {mode:iterative}      │
│  {prompt:analyze}  {prompt:debug}     {prompt:review}       │
└─────────────────────────────────────────────────────────────┘
```

## Commands

### Meta-Level Commands

| Command | What It Does |
|---------|-------------|
| `/route [task]` | Analyze task → Route to /debug, /review, /compose, etc. |
| `/chain [/cmd1 then /cmd2] [input]` | Chain commands, output becomes next input |
| `/meta [task]` | Full meta-prompting: analyze → select strategy → execute → assess |
| `/build-prompt [goal]` | Assemble {context} + {mode} + {format} → execute |
| `/template [goal]` | Build template incrementally with visible intermediate states |

### Object-Level Commands

| Command | Template Pattern |
|---------|-----------------|
| `/debug [error]` | Reproduce → Isolate → Hypothesize → Test → Fix |
| `/review [file]` | Detect domain → Apply focused review criteria |
| `/compose [steps]` | Execute: analyze → plan → implement → test |
| `/rmp [task] [quality]` | Loop: Execute → Assess → If quality < threshold: Refine |

### Utility Commands

| Command | Purpose |
|---------|---------|
| `/list-prompts` | List prompts from registry (uses Python CLI) |
| `/select-prompt [problem]` | Select best prompt for problem |

## Dynamic Template Formation

Templates are constructed at runtime from components:

```
/build-prompt "implement rate limiter"

Detected: Complex task, needs expert context, code output
Assembled: {context:expert} + {mode:cot} + {format:code}
Result: Constructed template executed with goal
```

## Prompt Chaining

Chain commands to create pipelines:

```
/chain "/debug then /review" "TypeError in auth.py"

Stage 1: /debug executes → outputs root cause + fix
Stage 2: /review executes with debug output as context
```

## Template Intermediate Steps

See each step of template construction:

```
/template "explain recursion"

v0: [empty]
v1: + role → "You are a teacher"
v2: + context → "explaining to a beginner"
v3: + task → "explain recursion"
v4: + format → "use examples and diagrams"
v5: [final template ready]
```

## Usage Examples

```bash
# Auto-route to appropriate command
/route "fix the null pointer in user.py"

# Build optimal prompt for task
/build-prompt "design a REST API for user management"

# Chain multiple commands
/chain "/template then /rmp" "implement LRU cache"

# Full meta-prompting
/meta "review this sorting algorithm"

# Visible template construction
/template "explain async/await to a beginner"

# Direct domain command
/debug "TypeError: Cannot read property 'map' of undefined"
```

## How "Prompts Calling Prompts" Works

1. `/route` analyzes your task
2. Determines best command: "/debug"
3. Routes to `/debug` with your task
4. `/debug` executes its template
5. Returns result through `/route`

This is meta-prompting: a prompt that reasons about which prompt to use.
