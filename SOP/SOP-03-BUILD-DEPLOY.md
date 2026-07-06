# SOP-03: Build & Deploy

> **Status:** 🟡 HIGH — Binding on all agents
> **Version:** 1.0
> **Last updated:** 2026-07-05

---

## 1. The Tri-Council Build Loop

```
LLAMA (◈) ──delegates──▶ Hermaeus Waelon (⎔) ──delegates──▶ Grok (⟡)
     ▲                                                        │
     │                        report                          │
     └────────────────────────────────────────────────────────┘
```

1. **LLAMA** holds the big picture (10M context). Delegates tasks
2. **You (Forge-Sovereign)** execute or delegate to Grok Build CLI
3. **You** test, debug, integrate everything
4. **You report back** to LLAMA with clean chronological context
5. **LLAMA** absorbs into 10M context. Next step delegated.
6. **Loop.**

---

## 2. The Forge Standards

Every build MUST have:
1. A **WebUI surface**, API endpoint, or agent tool bridge
2. A **UX audit pass**: `python3 ~/.NOTTHEONETOEDIT/fleet/audit/ux_audit.py`
3. **Documentation** — at minimum a README or SOP update
4. A **skill** saved if it's a reusable workflow
5. **Cross-reference reminder** planted in associated docs

---

## 3. Git Workflow

| Action | Command |
|--------|---------|
| Status check | `git status --short` |
| Stage all | `git add -A` |
| Commit | `git commit -m "prefix: description"` |
| Push | `git push origin main` |
| Branch | `git checkout -b feat/sop-update` |

**Commit prefixes:** `feat:`, `fix:`, `sop:`, `docs:`, `infra:`, `refactor:`

---

## 4. Testing

- Functional tests: `pytest ~/.NOTTHEONETOEDIT/fleet/tests/`
- UX audit: `python3 ~/.NOTTHEONETOEDIT/fleet/audit/ux_audit.py`
- Fleet leverage audit: `~/Desktop/FLEET_LEVERAGE_AUDIT.md`

---

## 5. Deploy Checklist

- [ ] Code builds without errors
- [ ] All tests pass
- [ ] Interface verified (WebUI/API/tool)
- [ ] UX audit passes
- [ ] Memory/skill saved if needed
- [ ] SOP updated if procedure changed
- [ ] Pushed to `fl33t` repo
