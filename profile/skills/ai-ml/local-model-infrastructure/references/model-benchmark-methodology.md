# Model Benchmark Methodology

## When to Use
A new GGUF model is available in `~/models/` and needs evaluation before fleet promotion. Run this on every candidate.

## Standard Test Suite

Run each test across **all active fleet models** for direct comparison.

### 1. Simple Command
Prompt: `"Write a one-line bash command to find all files modified in the last 24 hours. Just the command."`
Measures: basic instruction following, wall time, t/s

### 2. JSON Extraction
Prompt: `"Extract: name=Alice age=30 city=NYC. Return ONLY valid JSON."`
Measures: clean JSON output capability (Granite benchmark: passes as `{"name":"Alice","age":30,"city":"NYC"}`)

### 3. Clean JSON Output
Prompt: `"Convert to JSON: item=widget price=19.99 qty=3 in_stock=true"`
Measures: markdown-wrapped JSON, formatting quality

### 4. Reasoning
Prompt: `"How many 'r's are in 'strawberry'? Show your work in 1 line."`
Measures: reasoning capability (correct answer: 3 — but many models say 4 or 5)

### Measurement Protocol
```python
start = time.time()
r = terminal(command=f"""curl -s http://127.0.0.1:{port}/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {key}' \
  -d '{{"model":"model","messages":[{{"role":"user","content":{json.dumps(prompt)}}}],"max_tokens":{max_tokens}}}'""")
elapsed = time.time() - start
data = json.loads(r["output"])
content = data["choices"][0]["message"]["content"]
t = data.get("timings", {})
# Record: wall_clock_s, prompt_ms, predicted_ms, predicted_per_second (t/s)
```

## Metrics to Compare

| Metric | What It Tells You |
|--------|------------------|
| **t/s** (tokens/sec) | Raw throughput — higher = faster responses |
| **wall time** | Real-world latency the user experiences |
| **JSON quality** | `clean` (natively parsable), `wrapped` (needs extraction), `fail` |
| **Reasoning accuracy** | Integer counting, logic, chain-of-thought quality |
| **RSS** (resident set size) | Real RAM usage — `ps -p $PID -o rss` |
| **Model file size** | Disk footprint |
| **mmap efficiency** | Large models with mmap share disk cache; check `VmRSS` vs `VmSize` in `/proc/$PID/status` |

## Fleet Comparison Table Template

```
╔════════════════════╦═══════╦════════╦══════════════╗
║ Metric             ║ ModelA ║ ModelB ║ ModelC(NEW)  ║
╠════════════════════╬═══════╬════════╬══════════════╣
║ T/s                ║       ║        ║              ║
║ Simple cmd wall    ║       ║        ║              ║
║ JSON clean?        ║       ║        ║              ║
║ JSON wall          ║       ║        ║              ║
║ Reasoning pass?    ║       ║        ║              ║
║ RSS (MB)           ║       ║        ║              ║
╚════════════════════╩═══════╩════════╩══════════════╝
```

## Promotion Criteria
- If new model is **faster AND better** at the same role → replace the old one
- If new model has **unique capability** (clean JSON, uncensored, thinking chain) → keep alongside, assign distinct role
- **Critical finding (2026-07-18):** LFM 2.6B Uncensored (11.6 t/s, clean JSON, 2.0G file) made LFM 1.2B (3.0 t/s, wrapped JSON) and Granite 4.1 3B (1.3 t/s, clean JSON, 3.1G RSS) both redundant in a single benchmark run. Speed delta >5x can obsolete multiple fleet models.
