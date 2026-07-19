# Work Order Pattern

**Origin:** User correction in 2026-07-17 upgrade session. The pattern: "delete dead skills, form this shit out into work orders that contain the data necessary to complete that work order."

## Rule

When a system change has multiple steps (audit, compile, merge, delete, configure), **write a self-contained work order file** rather than narrating the plan. The next agent (or the same agent after context loss) runs the work order cold.

## Format

Each work order file contains **everything needed to execute independently**:

```markdown
# Work Order: <Title>

## Objective
One-line summary of what this accomplishes and why.

## Dependencies
What must be true before starting (installed packages, binaries, config state, prior work orders).

## Step-by-Step Execution
Numbered steps with exact commands, file paths, and flags. Every `cd`, `fpc`, `hermes config set`, `skill_manage`, `npm run build`, etc.

### Step N: Action
```bash
# Exact command to run
hermes config set compression.threshold 0.25
```

## Verification
Commands to confirm the work order completed successfully. Expected outcomes documented so the executor knows what "done" looks like.

## Token Impact (optional)
If this work order saves tokens, quantify it. E.g., "25 skills × ~1,200 avg tokens = 30,000 tokens → 5 skills × 1,200 = 6,000 tokens. Savings: 24,000 tokens (~$7.20/session at $300/1M)."
```

## Why Not Just Chat?

- **Context persistence:** A chat plan is lost when context compresses or the session ends. A file on disk survives.
- **Cold-start readiness:** Any agent (or a human) can execute a work order without re-reading the conversation history.
- **Verification built-in:** The verification step catches mistakes before they compound.
- **Batched execution:** Multiple work orders can be queued and executed by different agents in parallel.

## Location

All work orders live under `~/projects/hermes-upgrades/work-orders/`. Named `WO-NN_<short-description>.md` where NN is a zero-padded sequence number.
