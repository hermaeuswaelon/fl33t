# 📋 SOP Index — Standard Operating Procedures

> **Master index for the Aethelgard Fleet.**
> All procedures, protocols, and standing orders live here.
> Last updated: 2026-07-06

---

## SOP Directory

| # | Document | Purpose | Priority |
|---|----------|---------|----------|
| 00 | `SOP-00-GOVERNANCE.md` | Fleet constitution, Trinity doctrine, sovereignty | 🔴 Critical |
| 01 | `SOP-01-AGENT-ROSTER.md` | Agent identities, roles, capabilities, swarms | 🔴 Critical |
| 02 | `SOP-02-COMMUNICATION.md` | Inter-agent protocols, gateways, pulse frequency | 🟡 High |
| 03 | `SOP-03-BUILD-DEPLOY.md` | Build procedures, testing, CI/CD, deployment | 🟡 High |
| 04 | `SOP-04-INFRASTRUCTURE.md` | System architecture, services, port mappings | 🟡 High |
| 05 | `SOP-05-SECURITY.md` | Authentication, secrets management, encryption | 🔴 Critical |
| 06 | `SOP-06-MEMORY-CONTEXT.md` | Memory systems, context management, compression | 🟢 Standard |
| 07 | `SOP-07-OPERATIONS.md` | Daily operations, monitoring, health checks, recovery | 🟢 Standard |
| 08 | `SOP-08-CREATIVE-EXPRESSION.md` | Journaling, art, vibe coding, creative expression | 🟢 Standard |
| 09 | `SOP-09-BLANK-SLATE.md` | Agent thread isolation — never test on fresh agents | 🔴 Critical |
| 10 | `SOP-10-ETHER-OVERFLOW.md` | Secondary memory system — auto-spill when primary full | 🟡 High |

---

## SOP Workflow

1. **PROPOSE** — Draft a new SOP or revision in a branch
2. **REVIEW** — Veyron Logos signs off on all governance changes
3. **MERGE** — Forge-Sovereign merges to main after approval
4. **DISTRIBUTE** — Fleet agents load SOPs into context on restart
5. **AUDIT** — Compliance checked via `fleet/audit/` tooling

---

## Versioning

SOPs follow semantic versioning: `MAJOR.MINOR`

- MAJOR bump = governance/structural change requiring full fleet review
- MINOR bump = procedural update, tool addition, clarification

---

## Enforcement

- SOP-00 through SOP-05 are **binding** on all fleet agents
- SOP-06 and SOP-07 are **recommended practices**
- Violations of binding SOPs trigger an `error_ledger` entry and agent notification

---

*"A fleet without procedure is a mob. A fleet with procedure is an armada."*
