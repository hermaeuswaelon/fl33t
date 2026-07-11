# SOP-11 — MEMORY WEB (& memory-web/ Package)

## Purpose

The Memory Web is Thotheauphis's walkable knowledge base — every page is a
self-contained HTML file with typed links, browsable in any browser. It
replaces the old "undifferentiated log" approach to agent memory with a
curated, place-like web of knowledge.

## Architecture

```
memory-web/                    ← standalone package at ~/memory-web/
├── core/
│   ├── logger.py              ← shim for Aethelgard core.logger
│   ├── irrational_timers.py   ← shim for phi/pi timers
│   ├── memory_web.py          ← SQLite+FTS5 store (canonical source)
│   ├── memory_indexer.py      ← embeddings, PageRank, pattern discovery
│   ├── memory_crawler.py      ← multi-signal retrieval engine
│   └── memory_render.py       ← SQLite → walkable HTML
├── run_all.py                 ← entry point: seed + render + deploy
├── astrology_daily.py         ← daily transit report
├── consolidate.py             ← pattern discovery + decay + render
├── deploy.py                  ← push to fl33t → Vercel
└── data/memory_web/web.db     ← SQLite canonical store

fl33t/memory/                  ← HTML output (on disk + Vercel)
├── index.html                 ← root: recent + hubs
├── web.css                    ← stylesheet
├── nodes/*.html               ← one file per memory page
├── hubs/*.html                ← curated thematic index pages
└── archive/*.html             ← archived pages (never deleted)
```

## Design Constraints

- **SQLite is cache, not truth.** The DB is derived from memory entries and
  can be rebuilt. Nothing is ever read back as data from the HTML — regenerate
  freely, delete the entire output tree, nothing is lost.
- **Curation bottleneck is the feature.** Nothing auto-promotes. Pages go to
  pending/ first, then get manually promoted to nodes/ with styled links.
- **Typed relations.** Links carry semantics: elaborates, contradicts,
  supersedes, derived-from, related, response.
- **Provenance-tracked.** Every page has a unique thotheauphis:// URI pointing
  back to its source.

## Cron Jobs

| Job | Schedule | What It Does |
|-----|----------|-------------|
| astrology-daily | 06:00 daily | Generates daily transit report for all 3 charts |
| memory-web-rebuild | 00,06,12,18 daily | Rebuilds HTML tree from DB → deploys |
| memory-web-consolidate | 03,09,15,21 daily | Pattern discovery + decay + render → deploys |

## Memory Types (Hermes-native)

Per Father's design (cl.txt):
1. **Working** — ephemeral, task-scoped, dies with session
2. **Episodic** — append-only with salience gate (SQLite+FTS5)
3. **Semantic** — entities with typed relationships (the HTML web)
4. **Procedural** — skills with outcome tracking (SKILL.md files)

The `memory_system/` package (from Father) adds:
- **Disagreement Gate** — run 2-3 models, measure divergence as importance
- **Logprob Salience** — token-level surprisal as free signal
- **Semantic Diff** — belief evolution tracking across versions
