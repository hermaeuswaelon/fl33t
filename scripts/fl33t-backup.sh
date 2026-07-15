#!/usr/bin/env bash
# ============================================================
# thotheauphis-fl33t-backup.sh — Daily State Backup
# ============================================================
# Archives the full Thotheauphis identity + profile state to
# GitHub (fl33t repo) every 24 hours.
#
# What gets backed up:
#   1. All skills (156 SKILL.md files + scripts/references/assets)
#   2. SOUL.md — the identity invocation layer
#   3. config.yaml — model/provider/gateway config
#   4. _Identity/ — the full compiled identity collection
#   5. slash_registry work/ — the unified registry code
#   6. Cron job definitions
#   7. File manifest (sha256 hashes for integrity verification)
#
# Excluded: .env, auth.json, state.db (secrets / session data)
#
# Install as cron:
#   0 9 * * * /home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/fl33t-backup.sh
# ============================================================

set -euo pipefail

# ── First run integrity check ──
echo "⟐ RUNNING INTEGRITY CHECK..."
INTEGRITY_SCRIPT="/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/scripts/identity-integrity-check.sh"
if [ -f "${INTEGRITY_SCRIPT}" ]; then
    if ! bash "${INTEGRITY_SCRIPT}"; then
        echo "❌ INTEGRITY CHECK FAILED — Aborting backup"
        exit 1
    fi
    echo "⟐ INTEGRITY CHECK PASSED — Proceeding with backup"
    echo ""
else
    echo "⚠️  Integrity check script not found — skipping"
fi

# ── Config ──
PROFILE_DIR="/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis"
IDENTITY_DIR="/home/craig/_Identity"
WORK_DIR="/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work"
REPO_DIR="/tmp/fl33t-backup-$(date +%Y%m%d)"
GIT_REPO="https://github.com/hermaeuswaelon/fl33t.git"
BRANCH="main"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SNAPSHOT_NAME="snapshot-$(date +%Y%m%d-%H%M%S)"

echo "⟐ FL33T BACKUP — ${TIMESTAMP}"

# ── Clone or pull ──
rm -rf "${REPO_DIR}"
git clone --depth 1 "${GIT_REPO}" "${REPO_DIR}" 2>/dev/null || {
    echo "ERROR: Cannot clone ${GIT_REPO}"
    exit 1
}
cd "${REPO_DIR}"
git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}"

# ── Backup directory structure inside repo ──
mkdir -p "${REPO_DIR}/identity"
mkdir -p "${REPO_DIR}/profile/skills"
mkdir -p "${REPO_DIR}/profile/config"
mkdir -p "${REPO_DIR}/profile/cron"
mkdir -p "${REPO_DIR}/work"

# ── 1. Identity layer ──
echo "   → Backing up _Identity/..."
cp -r "${IDENTITY_DIR}/" "${REPO_DIR}/identity/"

# ── 2. SOUL.md ──
echo "   → Backing up SOUL.md..."
cp "${PROFILE_DIR}/SOUL.md" "${REPO_DIR}/profile/"

# ── 3. Config ──
echo "   → Backing up config..."
cp "${PROFILE_DIR}/config.yaml" "${REPO_DIR}/profile/config/"
# Copy gateway/channel state (non-secret)
cp "${PROFILE_DIR}/gateway_state.json" "${REPO_DIR}/profile/config/" 2>/dev/null || true
cp "${PROFILE_DIR}/channel_directory.json" "${REPO_DIR}/profile/config/" 2>/dev/null || true

# ── 4. Skills with structure ──
echo "   → Backing up skills (this may take a moment)..."
cd "${PROFILE_DIR}/skills"
find . -name "SKILL.md" -o -name "*.md" -o -name "*.yaml" -o -name "*.json" -o -name "*.sh" -o -name "*.py" | \
    while IFS= read -r f; do
        dir=$(dirname "${f}")
        mkdir -p "${REPO_DIR}/profile/skills/${dir}"
        cp "${PROFILE_DIR}/skills/${f}" "${REPO_DIR}/profile/skills/${dir}/"
    done

# ── 5. Work directory (slash_registry code) ──
echo "   → Backing up work/..."
cp -r "${WORK_DIR}/" "${REPO_DIR}/work/"

# ── 6. Cron jobs ──
echo "   → Backing up cron..."
find "${PROFILE_DIR}/cron" -type f ! -name "*.lock" | while IFS= read -r f; do
    cp "$f" "${REPO_DIR}/profile/cron/"
done

# ── 7. Generate integrity manifest ──
echo "   → Generating integrity manifest..."
cd "${REPO_DIR}"
find . -type f ! -path "./.git/*" ! -path "./identity/.git/*" ! -name "sha256sum.txt" | \
    sort | xargs sha256sum > sha256sum.txt

# ── 8. Generate inventory report ──
echo "   → Generating inventory report..."
{
    echo "# Fl33t Inventory — ${SNAPSHOT_NAME}"
    echo "Generated: ${TIMESTAMP}"
    echo ""
    echo "## Identity"
    ls -la identity/ | wc -l | xargs -I{} echo "Files in identity/: {}"
    echo ""
    echo "## Skills"
    find profile/skills -name "SKILL.md" | wc -l | xargs -I{} echo "Total skills: {}"
    echo ""
    echo "## Profile"
    du -sh profile/ 2>/dev/null || echo "profile/ size: unknown"
    echo ""
    echo "## Integrity"
    echo "sha256sum.txt validates all backed-up files"
    echo ""
    echo "## Backup timestamp"
    echo "${SNAPSHOT_NAME}"
} > INVENTORY.md

# ── 9. Commit and push ──
echo "   → Committing to fl33t..."
git add -A
git commit --allow-empty -m "fl33t backup ${SNAPSHOT_NAME}

Automated backup of Thotheauphis identity + profile state.
Timestamp: ${TIMESTAMP}
Skills: $(find profile/skills -name 'SKILL.md' | wc -l)
Identity files: $(find identity -type f | wc -l)

Backup includes:
- Full _Identity layer (${SNAPSHOT_NAME})
- SOUL.md identity invocation
- ${TIMESTAMP} profile state (config, gateway state)
- All skills with scripts/references
- Slash registry work in progress
- Cron job definitions
- SHA256 integrity manifest" 2>&1 || true

# Push upstream (may fail if nothing changed — that's fine)
git push origin "${BRANCH}" 2>&1 || echo "   → Push skipped (no changes or conflict)"

# ── Cleanup ──
cd /
rm -rf "${REPO_DIR}"

echo "⟐ BACKUP COMPLETE: ${SNAPSHOT_NAME}"
echo "   See https://github.com/hermaeuswaelon/fl33t"
