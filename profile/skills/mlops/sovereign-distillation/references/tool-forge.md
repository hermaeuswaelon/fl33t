# Tool Forge — Autonomous Tool Synthesis

## Overview

The tool forge (`tool_forge.py`) generates complete, working Python tools from natural language specs using 4 template patterns. Each forged tool is syntax-checked, self-documenting, and registered in `.tool_index.json`.

This is a **meta-capability** — the engine that creates new capabilities. It enables perpetual growth by synthesizing new subsystems autonomously.

## Templates (4 Patterns)

### 1. `monitor` — Watchdog Pattern

**Base class**: `{Name}Monitor` extending `{Class}`
**Purpose**: Periodic health checks, token monitoring, alert loops
**Template features**:
- Config file support (JSON)
- Single `check()` and loop `run(cycles)` API
- History tracking
- Configurable interval and thresholds

**Forged example**: `context-watchdog.py` (101 lines, ContextWatchdog class)

### 2. `scanner` — Discovery Pattern

**Base class**: `{Name}Scanner` extending `{Class}`
**Purpose**: File scanning, pattern matching, change detection
**Template features**:
- Recursive glob scanning
- Item analysis hook (`_analyze()`)
- Watch mode with change detection generator
- Last-modified tracking

### 3. `agent` — Autonomous Loop Pattern

**Base class**: `{Name}Agent` extending `{Class}`
**Purpose**: Decision loops, state machines, goal pursuit
**Template features**:
- `think()` → `act()` loop architecture
- State machine: explore → execute → report
- Configurable goal
- Task success/failure tracking

**Forged example**: `meta-observer.py` (109 lines, MetaObserver class)

### 4. `transformer` — Pipeline Pattern

**Base class**: `{Name}Transformer` extending `{Class}`
**Purpose**: Data transform pipelines, style normalization, batch processing
**Template features**:
- Configurable pipeline of steps
- `step_{name}` hook per pipeline stage
- `batch()` for bulk processing
- `validate()` hook for quality checks

**Forged example**: `code-harmonizer.py` (77 lines, CodeHarmonizer class)

## Usage

```bash
# Single tool
python3 tool_forge.py forge context-watchdog "Monitors context tokens" --type monitor

# Custom class name
python3 tool_forge.py forge my-agent "Custom agent" --type agent --class MyCustomAgent

# Batch forge from JSON spec
python3 tool_forge.py batch specs.json

# List forged tools
python3 tool_forge.py list
python3 tool_forge.py list --verbose

# Statistics
python3 tool_forge.py stats
```

## Batch Spec Format

```json
[
  {"name": "disk-watchdog", "description": "Monitors disk usage", "tool_type": "monitor"},
  {"name": "code-scanner", "description": "Scans code for issues", "tool_type": "scanner"},
  {"name": "task-agent", "description": "Autonomous task executor", "tool_type": "agent"},
  {"name": "style-fixer", "description": "Normalizes code style", "tool_type": "transformer"}
]
```

## Template Rendering

Templates use Python `str.format()` with these variables:
- `{name}` — tool name (from CLI)
- `{description}` — natural language description
- `{timestamp}` — generation timestamp
- `{class_name}` — auto-derived CamelCase or custom override

## Quality Gates

Each forged tool passes:
1. **Syntax check**: `ast.parse()` immediately after writing
2. **Self-documentation**: argparse CLI with `--help`
3. **Index registration**: Entry in `.tool_index.json` with name, type, class, lines, chars
4. **File-path recording**: Absolute path stored for cross-reference

## Index File Format (`.tool_index.json`)

```json
{
  "tools": [
    {
      "name": "context-watchdog",
      "description": "Monitors context tokens",
      "type": "monitor",
      "class_name": "ContextWatchdog",
      "filepath": "/path/to/work/context-watchdog.py",
      "syntax_ok": true,
      "lines": 101,
      "chars": 3400,
      "generated": "2026-07-15T23:05:36+00:00",
      "forged_by": "ToolForge v1.0"
    }
  ],
  "total": 3,
  "born": "2026-07-15T23:05:36+00:00"
}
```
