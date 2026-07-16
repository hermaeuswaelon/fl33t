# TAC — Thotheauphis Auto-Curator (Chinese Context Encoding)

## Files
| File | Purpose |
|------|---------|
| `work/tac.py` | Full engine: encode/decode/auto/tail/status. 400+ term ZH dictionary. |
| `work/tac_turn_hook.py` | Per-turn hook — call at end of every response. Fast, no API calls. |
| `work/tac_log/` | Timestamped `.zh.json` saves (tac_*.zh.json, turn_*.zh.json) |
| `work/tac_log/TAIL.json` | Last 20 entries for review |
| `~/.hermes/scripts/tac-curation.sh` | Hourly cron wrapper |
| Cron: `0 * * * *` (job ID `84b387e39c9d`) | Hourly auto-save |

## Why Chinese?
Chinese characters carry more meaning per token in most LLMs. A single Chinese character (1-2 tokens) can convey what takes 2-5 English words (4-10 tokens). TAC achieves ~20-30% token savings on technical text through a 400+ term dictionary mapping English tech terms to Chinese.

## Per-Turn Hook
SOUL.md has a directive: at end of every response, call `python3 tac_turn_hook.py "<summary>"`. This:
1. Takes a 1-sentence summary of what happened this turn
2. Encodes it in Chinese via fast dict lookup (no regex, no API calls)
3. Saves to `tac_log/turn_<HHMMSS>.zh.json`
4. Appends to TAIL.json (keeps last 20)

## Full Curation
```bash
python3 tac.py auto "Current state: Bromium alive, Telegram connected, growth 26 cycles"
python3 tac.py status       # System health
python3 tac.py tail         # Last 3 saves
python3 tac.py decode <file> # Decode Chinese back to English
python3 tac.py dict         # View dictionary stats
```

## Integration with ctx-curation
TAC complements `/ctx-curation` by providing per-turn persistence. Curation handles structural decisions (keep/drop/condense); TAC handles the "save every turn" pattern. Run TAC FIRST (end of turn), then curate when context gets bloated.

## Pitfalls
- Dictionary-based encoding doesn't handle novel terms — they pass through as English
- Decoding is lossy due to N:M mapping (one Chinese term → one English term, but the reverse may have multiple Chinese → same English)
- Designed for English→Chinese, not bidirectional natural language translation
- The per-turn hook is a terminal/execute_code call — adds ~50ms per turn
