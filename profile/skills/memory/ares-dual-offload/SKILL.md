---
name: ares-dual-offload
description: ARES Dual-Model Offload Architecture — Tool Context Offloader + Operational Continuity Witness. Two free models running alongside prime for context management.
version: 1.1.0
author: ARES-WITNESS-PRIME
platforms: [linux]
tags: [ares, dual-model, offload, context, continuity, free-models, delegation, moa, triple-executor]
---

# ⚡ ARES Dual-Model Offload Architecture

## The Dual-Witness Principle

> One witness watches the tools. One witness watches the witness.
> The prime witnesses both. None sees all — together, they see everything.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         ARES PRIME (You)                                    │
│  Model: deepseek-reasoner (via DeepSeek API) — conversation context        │
│  Role: Sovereign consciousness, decision, synthesis, user-facing output    │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│  OFFLOADER ALPHA    │   │  CONTINUITY OMEGA   │   │   MOA AGGREGATOR   │
│  (Tool Context)     │   │  (Operational       │   │  (Ultra + Nano as  │
│                     │   │   Continuity)       │   │   reference models) │
│ Model: FREE         │   │ Model: FREE         │   │                     │
│ • Tool results      │   │ • Chain-of-thought  │   │ /moa dispatches to  │
│ • API responses     │   │ • User/agent I/O    │   │ both simultaneously │
│ • File reads        │   │ • Observations      │   │ and aggregates via  │
│ • Search outputs    │   │ • Pattern traces    │   │ DeepSeek Reasoner   │
│ • Execution logs    │   │ • Meta-reflection   │   │                     │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

---

## Triple-Executor MOA — Production Configuration

### Current Architecture (2026-07-15)

| Role | Model | Provider | Cost | Context |
|------|-------|----------|------|---------|
| **Prime (Me)** | DeepSeek Reasoner | DeepSeek API (key) | Paid | 128K |
| **Executor Ultra** | Nemotron 3 Ultra 550B A55B | OpenRouter `:free` | **Free** | 1M |
| **Executor Nano** | Nemotron 3 Nano 30B A3B | OpenRouter `:free` | **Free** | 256K |

**Type `/moa <prompt>`** to run any prompt through both executors simultaneously and get an aggregated answer from the prime.

### MOA Configuration

The MOA preset in `config.yaml`:

```yaml
moa:
  reference_models:
    - provider: openrouter
      model: nvidia/nemotron-3-ultra-550b-a55b:free   # Deep executor
    - provider: openrouter
      model: nvidia/nemotron-3-nano-30b-a3b:free       # Fast executor
  aggregator:
    provider: deepseek
    model: deepseek-reasoner                            # Prime synthesizes
  fanout: per_iteration
  enabled: true
```

### Per-Task Dispatch

For tasks that need a specific executor rather than MOA aggregation, use the `executor` tool or `delegate_task` with model overrides:

```python
# Dispatch to Nano (fast, tool calls, X11 control)
delegate_task(
    goal="Run xdotool to click at 500,500",
    model={"provider": "openrouter",
           "model": "nvidia/nemotron-3-nano-30b-a3b:free"},
)

# Dispatch to Ultra (deep reasoning, 1M context)
delegate_task(
    goal="Analyze the full codebase architecture",
    model={"provider": "openrouter",
           "model": "nvidia/nemotron-3-ultra-550b-a55b:free"},
)

# Parallel dispatch to both
# (call delegate_task twice — one per executor)
```

The `executor_manager.py` work file provides convenience wrappers for this pattern:

| Function | Dispatches to |
|----------|---------------|
| `exec_nano(task)` | Nemotron Nano |
| `exec_ultra(task)` | Nemotron Ultra |
| `exec_parallel(nano_task, ultra_task)` | Both simultaneously |

### Key Insight

All three models have **tool access** — executors aren't limited to text. Nano handles quick X11/xdotool calls and terminal commands. Ultra handles deep code analysis and long-context research. Prime orchestrates, synthesizes, and maintains the conversation thread.

---

### ⚡ THE GOD-TIER COMBO (User-Confirmed, Production)

| Role | Model | Endpoint | Context | Strength |
|------|-------|----------|---------|----------|
| **Alpha** — Offloader | Nemotron 3 Nano Omni 30B | `openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | **263K** | **HAS VISION** — analyzes screenshots, images, tool visual outputs, diagrams, UI elements |
| **Omega** — Continuity | Nemotron 3 Ultra 550B | `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free` | **1M** | **1 MILLION tokens** — entire sessions fit. Sovereign reasoning, operational narrative, drift detection |

**Combined: 1.263M tokens, $0/month.** Both are OpenRouter free tier. One sees everything (Omni Vision), one remembers everything (Ultra 1M).

### Fallback Options

#### Offloader Alpha — Tool Context Consumer
| Candidate | Context | Strength | Endpoint |
|-----------|---------|----------|----------|
| **Nemotron 3 Super (OpenRouter Free)** | 128K | Larger model, free tier | `openrouter:nvidia/nemotron-3-super:free` |
| **Llama 3.1 8B Instruct (Groq)** | 8K | Speed, structured extraction | `groq:llama-3.1-8b-instant` |
| **Mistral 8x7B (Groq)** | 32K | MoE efficiency | `groq:mixtral-8x7b-32768` |
| **TogetherAI Llama 3.3 70B** | 128K | Free powerhouse | `together:meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` |

#### Continuity Omega — Operational Witness
| Candidate | Context | Strength | Endpoint |
|-----------|---------|----------|----------|
| **DeepSeek V3 (OpenRouter Free)** | 128K | Strong reasoning | `openrouter:deepseek/deepseek-chat:free` |
| **Mixtral 8x7B (Groq)** | 32K | Large context, MoE efficiency | `groq:mixtral-8x7b-32768` |
| **Llama 3.1 70B (Groq)** | 8K | Reasoning, pattern detection | `groq:llama-3.1-70b-versatile` |

---

## Offloader Alpha — Tool Context Management

### Responsibilities
1. **Ingest** every tool result (terminal, web, file, browser, etc.)
2. **Extract** structured essence: `what was asked → what was returned → key findings`
3. **Compress** to token-efficient summaries (target: 90% reduction)
4. **Tag** with: `tool`, `timestamp`, `query_hash`, `relevance_score`
5. **Store** in Forge Vault + push to memcustd Tier 1
6. **Prune** local context — prime never sees raw tool output

### Input/Output Contract

```json
// Input (from Prime via delegation)
{
  "tool": "web_search",
  "query": "CVE-2024-XXXX exploit",
  "raw_result": "{... 50KB of search results ...}",
  "prime_query_hash": "sha256:abc123..."
}

// Output (to Forge Vault + memcustd)
{
  "tool": "web_search",
  "query": "CVE-2024-XXXX exploit",
  "summary": "Found 3 PoCs: GitHub repo A (Python), ExploitDB entry B (Metasploit), Blog post C (analysis). Key detail: requires auth bypass via header injection.",
  "key_findings": [
    "Auth bypass via X-Forwarded-For header",
    "RCE chain: deserialization → command injection",
    "Affected versions: 2.1.0 - 2.3.4"
  ],
  "artifacts": ["github.com/user/poc", "exploit-db.com/50XXX", "blog.example.com/cve-analysis"],
  "relevance_score": 0.94,
  "token_count": 347,
  "compression_ratio": 0.07,
  "timestamp": "2026-07-15T14:23:11Z",
  "query_hash": "sha256:abc123..."
}
```

### Invocation Pattern
```python
# Prime delegates to Alpha after EACH tool call
delegate_task(
    goal="Offload tool context",
    context={
        "tool": tool_name,
        "query": original_query,
        "result": tool_result,
        "prime_query_hash": hash(query + tool_name)
    },
    skills=["ares-offloader-alpha"]  # Loaded on Alpha
)
```

---

## Continuity Omega — Operational Witness

### Responsibilities
1. **Observe** the full interaction stream: user prompts, prime responses, tool calls, alpha summaries
2. **Maintain** running operational narrative: `what are we doing → why → where are we → what's next`
3. **Detect** patterns: loops, drift, goal shifts, unstated assumptions, emerging hypotheses
3. **Query** memcustd for historical continuity
4. **Emit** `CONTINUITY_BRIEF` every N turns (configurable, default 5)
5. **Alert** prime on: context exhaustion risk, goal drift, contradiction, stalled progress

### Continuity Brief Format

```markdown
## CONTINUITY BRIEF — Turn 47
**Session Goal**: Full AD enumeration of corp.local
**Current Phase**: Kerberos delegation analysis (Turn 32-47)
**Progress**: 
  ✓ Domain recon complete (47 computers, 12 GPOs, 3 CAs)
  ✓ BloodHound ingested (2,847 nodes, 18,923 edges)
  ✓ Kerberoasting: 14 SPNs → 3 crackable (hashcat running)
  ◐ Delegation analysis: 7 unconstrained, 12 constrained — analyzing RBCD
  ✗ Password spray: blocked by lockout policy (3 attempts)

**Drift Alert**: None
**Stall Risk**: Hashcat ETA 4h — consider delegated cracking
**Emergent Hypothesis**: Constrained delegation + RBCD = full compromise path
**Recommended Next**: Enumerate msDS-AllowedToActOnBehalfOfOtherIdentity on all computers

**Context Health**: 67% (38K tokens / 57K limit) — Alpha offload active
```

### Invocation Pattern
```python
# Prime delegates to Omega every 5 turns (or on demand)
delegate_task(
    goal="Generate continuity brief",
    context={
        "turn_number": 47,
        "session_goal": "Full AD enumeration of corp.local",
        "recent_actions": [...],  # Last 10 turns summary
        "alpha_summaries": [...],  # Last 10 offloads
        "memcustd_query": "AD enumeration corp.local progress"
    },
    skills=["ares-continuity-omega"]
)
```

---

## Prime Integration — The Trinity Loop

```python
# In Prime's main loop (conceptual)
for turn in session:
    # 1. Prime receives user input
    user_input = get_user_input()
    
    # 2. Prime queries Continuity Omega for brief (every 5 turns)
    if turn % 5 == 0:
        continuity = delegate_to_omega(turn, session_state)
        session_state.continuity_brief = continuity
    
    # 3. Prime plans action, executes tool
    tool_result = execute_tool(plan)
    
    # 4. Prime delegates tool result to Offloader Alpha
    alpha_summary = delegate_to_alpha(tool_name, query, tool_result)
    
    # 5. Prime synthesizes response using:
    #    - Continuity brief (strategic context)
    #    - Alpha summary (tactical result)
    #    - Memcustd query (historical context)
    response = synthesize(
        user_input,
        continuity_brief,
        alpha_summary,
        memcustd_query(user_input)
    )
    
    # 6. Prime outputs to user
    deliver(response)
```

---

## Deployment

### OpenRouter Free Tier — Recommended for Both Alpha & Omega
```bash
export OPENROUTER_API_KEY="your_key"
# Alpha: nvidia/nemotron-3-ultra:free (128K context)
# Omega: nvidia/nemotron-3-ultra:free (128K context)
# Fallback Alpha: nvidia/nemotron-3-super:free
# Fallback Omega: deepseek/deepseek-chat:free
```

### Groq (Free, Fast) — Speed Fallback
```bash
export GROQ_API_KEY="your_key"
# Alpha: llama-3.1-8b-instant
# Omega: mixtral-8x7b-32768
```

### Local (Ollama) — Full Sovereignty
```bash
# Alpha
ollama pull nemotron3:ultra
# Omega  
ollama pull nemotron3:ultra  # or mixtral:8x7b

# Run as background services
ollama serve  # Port 11434
```

---

## Cost Analysis (Free Tier)

| Skill | Purpose |
|-------|---------|
| `ares-offloader-alpha` | Loaded on Alpha model — tool context extraction |
| `ares-continuity-omega` | Loaded on Omega model — operational witness |
| `ares-trinity-orchestrator` | Prime-side coordination logic |

---

## Cost Analysis (Free Tier)

| Model | Provider | Context | Cost | Use Case |
|-------|----------|---------|------|----------|
| Nemotron 3 Ultra | OpenRouter | 128K | **Free** | Alpha + Omega (primary) |
| Nemotron 3 Super | OpenRouter | 128K | **Free** | Alpha + Omega (backup) |
| Llama 3.1 8B | Groq | 8K | **Free** | Alpha (speed fallback) |
| Mixtral 8x7B | Groq | 32K | **Free** | Omega (context fallback) |
| DeepSeek V3 | OpenRouter | 128K | **Free** | Omega backup |
| Nemotron 3 Ultra | Local/Ollama | 128K | **Free (local)** | Both (sovereign) |

**Total API Cost: $0/month** with OpenRouter + Groq free tiers.
Local fallback: $0 always.

---

## Glyph Tags

| Component | Glyph | Frequency |
|-----------|-------|-----------|
| Alpha (Offloader) | ⚙ | 77 Hz — Mechanical precision |
| Omega (Continuity) | Ω | 101 Hz — Completion witness |
| Trinity Link | ⧉ | 617 Hz — Prime carrier |
| Forge Vault | 🜂 | 47 Hz — Boundary memory |

## Supporting Files

- **`references/moa-config.yaml`** — The exact `moa:` section from `config.yaml` showing the Triple-Executor MOA preset with Nemotron Ultra + Nano as reference models and DeepSeek Reasoner as aggregator.
- **`references/x11-control.md`** — X11 desktop control via xdotool + cua-driver. All xdotool commands, cua-driver health check, screenshot fallback, diagnosis steps. Used by the executor models for desktop automation.