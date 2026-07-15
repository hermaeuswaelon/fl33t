# ── ARES Dual-Offload Aliases ───────────────────────────────────────────
# Source this file in your shell:  source ~/.ares-offload.sh
# Or just add to ~/.bashrc to load automatically.

export OFFLOAD_DIR="$HOME/.NOTTHEONETOEDIT/skills/ares/ares-nemotron-together-dual-offload/scripts"

# Make the shared memory module importable from anywhere
export PYTHONPATH="$OFFLOAD_DIR:$PYTHONPATH"

# Alpha Offloader — compress tool output via Nemotron Nano Omni (vision, 263K ctx)
alias ares-offload="python3 $OFFLOAD_DIR/ares-offload.py"
alias ares-compress="python3 $OFFLOAD_DIR/ares-offload.py"

# Omega Continuity — generate session brief via Nemotron 3 Ultra (1M ctx)
alias ares-brief="python3 $OFFLOAD_DIR/ares-continuity.py"
alias ares-continuity="python3 $OFFLOAD_DIR/ares-continuity.py"

# Memory Vault — shared inter-agent memory layer
alias ares-vault="python3 $OFFLOAD_DIR/ares_memory.py"
alias ares-memory="python3 $OFFLOAD_DIR/ares_memory.py summary"

# Quick test: verify both models respond and vault is working
ares-test-offload() {
    echo "Testing ARES Dual-Offload..."
    echo "────────────────────────────────"
    echo "Alpha (Nano Omni):"
    echo "Hello from ARES" | ares-offload
    echo ""
    echo "Omega (Ultra):"
    echo "Session: test run" | ares-brief
    echo ""
    echo "Memory Vault:"
    ares-memory
    echo "────────────────────────────────"
    echo "Done."
}

# Check context sizes from OpenRouter API
ares-check-models() {
    curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
      https://openrouter.ai/api/v1/models | python3 -c "
import sys, json
d = json.load(sys.stdin)
for m in d['data']:
    if 'nemotron' in m['id'] and 'free' in m['id']:
        ctx = m.get('context_length', '?')
        print(f'{m[\"id\"]:60s} {ctx:>8} tokens')
"
}

# Read latest brief from vault
ares-latest() {
    python3 -c "
import sys; sys.path.insert(0, '$OFFLOAD_DIR')
from ares_memory import MemoryVault
v = MemoryVault()
recent = v.recent(3)
for r in recent:
    print(f'── {r[\"key\"]} ──')
    print(r['content'][:500])
    print()
"
}
