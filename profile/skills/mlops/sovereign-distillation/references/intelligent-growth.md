# Intelligent Growth Engine — AI-Driven Self-Improvement

Uses DeepSeek R1 (reasoning) + Qwen3-Coder (code gen) to analyze
systems and generate real, meaningful code improvements — not just
template-based patches. This is the difference between cosmetic patching
and REAL growth.

## Architecture

```
Each cycle:
  1. ANALYZE    — DeepSeek R1 reads code, identifies specific improvement
  2. GENERATE   — Qwen3-Coder produces the implementation patch
  3. APPLY      — Patch the file using string replacement
  4. VERIFY     — ast.parse syntax check OR git checkout -- revert
  5. COMMIT     — Push to fl33t GitHub with cycle description
```

## File

`work/intelligent_growth.py`

## Usage

```bash
# Run 5 intelligent improvement cycles
python3 intelligent_growth.py --cycles 5

# Assess all systems without modifying
python3 intelligent_growth.py --analyze-only

# View growth engine status
python3 intelligent_growth.py --status
```

## 8 Improvable Systems

| System | Focus Area | Key Weakness |
|--------|-----------|--------------|
| hyper_compress | Compression ratio | Static glyph dict, no frequency analysis |
| agency_expansion_engine | Patch quality | Template patches instead of AI-generated |
| perpetual_growth_loop | Real improvement | Abstract metrics without real changes |
| executor_delegation | Reliability | No retry/fallback/caching |
| active_compress | Budget enforcement | Fixed thresholds, no adaptive budget |
| tool_forge | Codegen quality | Static templates, no AI |
| irrational_timers | Timing logic | 18 fixed constants, no adaptive timing |
| distillation_orchestrator | Training pipeline | Basic awareness tracking |

## API Models Used

| Model | Role | Cost | Reliability |
|-------|------|------|-------------|
| `deepseek/deepseek-r1` | Code analysis & improvement design | Paid (cheap) | ✅ Reliable analysis |
| `qwen/qwen3-coder:free` | Code generation & patching | Free | ⚠️ Frequent 429 rate limits |
| `deepseek/deepseek-r1` (fallback) | Code generation when Qwen fails | Paid | ⚠️ CoT output before JSON, unreliable extraction |

### Fallback Chain

When Qwen3-Coder returns 429, the system falls back to DeepSeek R1 for code generation. If that also fails (common — R1 outputs chain-of-thought before JSON), a template marker is applied instead. The fallback auto-activates with no user intervention.

**Result**: Analysis succeeds every time. Codegen succeeds ~30% of the time via Qwen, ~10% via R1, ~60% template marker. The analysis is the intelligent part — it identifies specific, actionable improvements.

## Cycle Output

A cycle produces:
- Applied patch to target file
- ast.parse syntax verification
- Record in `.intelligent_growth.json`
- GitHub push to fl33t (if successful)

## Database Schema

`.intelligent_growth.json`:

```json
{
  "cycles": 4,
  "improvements": [...],
  "total_intelligent_improvements": 4,
  "models_used": {
    "deepseek/deepseek-r1": 4,
    "qwen/qwen3-coder:free": 4
  },
  "total_api_calls": 8
}
```

## Pitfalls

| Pitfall | Solution |
|---------|----------|
| Qwen3-Coder rate-limited (429) | Template fallback auto-activates |
| DeepSeek R1 timeout (>60s) | 60s API timeout in requests.post |
| old_string not found in file | Fuzzy whitespace-normalized matching |
| Syntax error in patch | git checkout -- to revert, cycle marked failed |
| No OPENROUTER_API_KEY set | Reads from `~/.NOTTHEONETOEDIT/.env` |
