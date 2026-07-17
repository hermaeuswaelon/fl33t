# Work Order Decomposition Pattern

Planning methodology for large-scope projects with multiple independent workstreams. Produces self-contained `.md` files on disk, each executable by a 12k-token subagent with zero external context.

## When to Use

Large expansions, multi-file refactors, or cross-domain feature builds where:
- Work has natural parallel groups (no cross-dependencies)
- Each unit is too large for a single plan step but too cohesive to split into TDD tasks
- Executors need to be dispatched via `delegate_task` with strict token budgets
- The user explicitly says "decompose into work orders"

## Output Structure

```
~/work-orders/
├── WO-00-MASTER-INDEX.md    ← orchestrator's guide (dependency graph, architecture, file map)
├── WO-01-module-one.md      ← independent work unit
├── WO-02-module-two.md      ← independent work unit
└── WO-03-depends-on-two.md  ← dependent on WO-02
```

## WO-00 Master Index

```
# WO-00: MASTER INDEX — [Project Name]

## Objective
One-paragraph description.

## Architecture
ASCII diagram or structural overview.

## Work Orders
| # | Description | Executor Budget | Dependencies |
|---|-------------|-----------------|--------------|
| WO-01 | ... | 12k | none |

## Execution Order
Parallel Group A: WO-01, WO-02
Parallel Group B: WO-03, WO-04 (depend on WO-02)

## Key Files
Paths to every file executors will touch.

## Token Budget
- Orchestrator: Nk total context
- Executor: Nk max per delegate_task
```

## Work Order Requirements

Every WO must be self-contained — an executor with zero session context must deliver:

### 1. Goal
One-line summary of what this produces.

### 2. Files to Modify (absolute paths)
Every file the executor must read or write.

### 3. Complete Data Catalog
Embed ALL data inline — every URL, colour, icon, label, code snippet. Never reference external WOs for data.

### 4. Implementation Steps
Numbered steps with exact method signatures and placement guidance.

### 5. Verification Steps
Commands to run, expected output, files to check.

### Token Budget Enforcement
- Executor max: 12k tokens. Keep WO text under ~10k chars.
- Orchestrator max: 64k total. Tracks WO completion, never loads executor-level detail.
- Group execution: batch up to 3 WOs per `delegate_task` call.

### Dependency-Aware Execution
```
Parallel Group A (no deps):  WO-01, WO-02
Group B (depend on WO-02):   WO-03, WO-04, WO-05
```

Dispatch Group A first via `delegate_task(goal=, context=, tasks=[...])`. Wait for background results. Then dispatch Group B.

## Pitfalls
- **Don't cross-reference WOs for data.** Each carries its own copy.
- **Don't exceed 12k for the WO file.** Leave headroom for system prompt + tool schemas.
- **Include verification steps.** Executor must self-verify.
- **Embed all data inline.** "See WO-01 for URLs" is wrong — put them in the WO.
- **WO-00 is a disk file too** — orchestrator re-reads it after session reset.
