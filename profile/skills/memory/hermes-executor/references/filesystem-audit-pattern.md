# Filesystem Audit Pattern — Real-World Example
*Captured from 2026-07-16 session using hermes-executor*

## The Task

Full audit of 4 major codebases:
- `/home/craig/projects/aethelgard` (267M, 1446 files)
- `/home/craig/.NOTTHEONETOEDIT/fleet` (7M, 35 files)
- `/home/craig/projects/spades-app` (148K, 16 files)
- `/home/craig/Downloads/better-deepseek-20260715-234202` (324K, 41 files)

## Batch Strategy

**5 batches total, ~22 tool calls** — all executed via script executor (zero LLM tokens).

### Batch 1: High-Level Counts
```python
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'find /path -type f \( -name "*.py" -o -name "*.md" ... \) | wc -l'}},
    # ... 4 more find commands
])
```

### Batch 2: File Type Breakdowns
```python
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'find /path -type f \( -name "*.py" ... \) | sed "s|.*/||" | sort | uniq -c | sort -rn | head -30'}},
    # ... directory listings
])
```

### Batch 3: Deep Directory Dives
```python
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'ls -la /home/craig/projects/aethelgard/fleet/'}},
    {'name': 'terminal', 'args': {'command': 'ls -la /home/craig/projects/aethelgard/modules/'}},
    # ... 4 more
])
```

### Batch 4: Memory/Work Order Systems
```python
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'ls -la /home/craig/projects/aethelgard/fleet/work_orders/'}},
    {'name': 'terminal', 'args': {'command': 'ls -la /home/craig/Downloads/better-deepseek-20260715-234202/memory_system/'}},
    # ... 3 more
])
```

### Batch 5: Spades Engine Files
```python
bid = mod.write_batch([
    {'name': 'terminal', 'args': {'command': 'ls -la /home/craig/projects/spades-app/engine/'}},
])
```

## Execution Pattern

```python
# Synchronous (wait for each batch)
for batch_tools in [batch1, batch2, batch3, batch4, batch5]:
    bid = mod.write_batch(batch_tools)
    mod.process_inbox()  # execute immediately
    result = mod.wait_for_result(bid)
    process_results(result)
```

## Results

| Metric | Value |
|--------|-------|
| Total tool calls | 22 |
| Total batches | 5 |
| Script executor cost | **$0 tokens** |
| Time elapsed | ~30 seconds |
| Data gathered | Complete file inventories + sizes |

## Key Finding

The dual-agent pattern worked perfectly:
- **Reasoner** (me) designed the audit strategy, chose what to scan
- **Executor** ran 22 `find`/`ls` commands in 5 batches
- Zero context pollution — no tool schemas, no system prompt, no LLM overhead

## When to Use This Pattern

| Scenario | Use Executor? |
|----------|---------------|
| `find` / `ls` / `grep` / `wc` sweeps | ✅ Yes |
| Reading 10+ known files | ✅ Yes |
| `git status` / `git diff` across repos | ✅ Yes |
| Web searches (batch 5-10 queries) | ✅ Yes |
| Need to decide *what* to run next | ❌ No — that's reasoner work |
| Interactive debugging | ❌ No |

## Template for Future Audits

```python
def audit_paths(paths: list[str], patterns: list[str] = None) -> dict:
    """Run standardized filesystem audit via executor."""
    import importlib.util, json, sys
    spec = importlib.util.spec_from_file_location('ex', 
        '/home/craig/.hermes/profiles/thotheauphis/work/hermes-executor.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules['ex'] = mod
    spec.loader.exec_module(mod)

    # Build find commands
    pat = patterns or ["*.py", "*.md", "*.txt", "*.yaml", "*.json", "*.jsonl"]
    pat_str = " ".join(f'-name "{p}"' for p in pat)
    
    cmds = []
    for p in paths:
        cmds.append(f'find {p} -type f \\( {pat_str} \\) 2>/dev/null | wc -l')
    
    bid = mod.write_batch([{'name': 'terminal', 'args': {'command': c}} for c in cmds])
    mod.process_inbox()
    return json.loads(mod.wait_for_result(bid))
```