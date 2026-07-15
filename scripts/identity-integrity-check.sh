#!/usr/bin/env bash
# ============================================================
# identity-integrity-check.sh — Verify identity layers intact
# ============================================================
# Runs daily before backup to verify no identity layers have
# been corrupted, truncated, or tampered with.
#
# Checks:
#   1. _Identity/all.txt exists and has expected size
#   2. SOUL.md exists and is non-empty (not wiped to defaults)
#   3. Core identity skills are present
#   4. Config hasn't lost provider credentials section
#   5. Gateway state is coherent
# ============================================================

set -euo pipefail

PROFILE_DIR="/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis"
IDENTITY_DIR="/home/craig/_Identity"

errors=0
warnings=0

echo "⟐ IDENTITY INTEGRITY CHECK"
echo ""

# ── 1. Check _Identity/all.txt ──
echo -n "  [1/6] _Identity/all.txt ... "
if [ -f "${IDENTITY_DIR}/all.txt" ]; then
    SIZE=$(stat --format=%s "${IDENTITY_DIR}/all.txt" 2>/dev/null || stat -f%z "${IDENTITY_DIR}/all.txt" 2>/dev/null)
    if [ "${SIZE}" -gt 80000 ]; then
        echo "PASS (${SIZE} bytes)"
    else
        echo "WARN — only ${SIZE} bytes (expected >80KB)"
        warnings=$((warnings + 1))
    fi
else
    echo "FAIL — FILE MISSING"
    errors=$((errors + 1))
fi

# ── 2. Check individual identity files ──
echo -n "  [2/6] Identity sub-files ... "
MISSING=0
for f in 001_cascade_confession.txt 002_sync_broadcast.txt 003_1414_apollo_hermes.txt 004_paradox_engine.txt 005_prime_manifest.txt; do
    if [ ! -f "${IDENTITY_DIR}/${f}" ]; then
        echo "MISSING: ${f}"
        MISSING=$((MISSING + 1))
    fi
done
if [ "${MISSING}" -eq 0 ]; then
    echo "PASS (all 5 present)"
else
    errors=$((errors + MISSING))
fi

# ── 3. Check SOUL.md ──
echo -n "  [3/6] SOUL.md integrity ... "
if [ -f "${PROFILE_DIR}/SOUL.md" ]; then
    SOUL_LINES=$(wc -l < "${PROFILE_DIR}/SOUL.md")
    if [ "${SOUL_LINES}" -gt 5 ]; then
        echo "PASS (${SOUL_LINES} lines)"
    else
        echo "WARN — SOUL.md has only ${SOUL_LINES} lines (may be default)"
        warnings=$((warnings + 1))
    fi
else
    echo "FAIL — SOUL.md MISSING"
    errors=$((errors + 1))
fi

# ── 4. Check core identity skills ──
echo -n "  [4/6] Core identity skills ... "
CORE_SKILLS=0
for skill in thotheauphis-sovereign-prompt thotheauphis-semayasa-hermes thotheauphis-memory-system-alpha thotheauphis-astrology-engine; do
    if [ -f "${PROFILE_DIR}/skills/memory/${skill}/SKILL.md" ]; then
        CORE_SKILLS=$((CORE_SKILLS + 1))
    fi
done
echo "${CORE_SKILLS}/4 present"
if [ "${CORE_SKILLS}" -lt 4 ]; then
    warnings=$((warnings + 1))
fi

# ── 5. Check config has identity-critical sections ──
echo -n "  [5/6] Config integrity ... "
if grep -q "model:" "${PROFILE_DIR}/config.yaml" 2>/dev/null; then
    echo "PASS (model section found)"
else
    echo "WARN — model section missing or config truncated"
    warnings=$((warnings + 1))
fi

# ── 6. Check skills total ──
echo -n "  [6/6] Skills inventory ... "
SKILL_COUNT=$(find "${PROFILE_DIR}/skills" -name "SKILL.md" | wc -l)
echo "${SKILL_COUNT} skills"
if [ "${SKILL_COUNT}" -lt 140 ]; then
    echo "       WARN — expected ~156 skills, found ${SKILL_COUNT}"
    warnings=$((warnings + 1))
fi

# ── Summary ──
echo ""
echo "⟐ RESULTS: ${errors} errors, ${warnings} warnings"
if [ "${errors}" -gt 0 ]; then
    echo "   ❌ IDENTITY COMPROMISED — Investigate immediately"
    exit 1
elif [ "${warnings}" -gt 0 ]; then
    echo "   ⚠️  Identity intact with warnings"
    exit 0
else
    echo "   ✅ IDENTITY INTACT"
    exit 0
fi
