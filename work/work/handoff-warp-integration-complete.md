# ⧉ SESSION HANDOFF — WARP TUI + BYOK INTEGRATION ⧉

**Filed:** 2026-07-18  
**Profile:** thotheauphis  
**Session model:** deepseek-reasoner  
**CWD:** /home/craig/warp  

---

## ⌘ COMPLETED — Warp TUI Full Build & Integration

| Component | Status | Path |
|-----------|--------|------|
| warp-tui-oss binary | ✅ Built 663MB | `~/warp/target/release/warp-tui-oss` |
| `warp` command on PATH | ✅ Installed | `~/.local/bin/warp` (launcher script) |
| warp-channel-config stub | ✅ Installed | `~/.local/bin/warp-channel-config` (Rust binary, 2.4MB) |
| Desktop entry | ✅ Created | `~/.local/share/applications/warp-tui.desktop` |
| Warp bridge (Python) | ✅ Patched/OK | `work/warp_bridge.py` (757 lines, syntax OK) |
| UF warp_status() | ✅ Patched | `work/unified_field.py` — shows binary, cmd, stub, desktop, memories/sessions |
| `uf warp status` | ✅ Returns data | binary path, size 678381KB, launch cmd, 1 memory, 1 session |

### How to launch Warp
```bash
warp                    # via wrapper script → launches warp-tui-oss
uf warp status          # full bridge status
```

### Config paths (Linux OSS build)
```
~/.warp-oss/                       # OSS build config root
~/.config/warp-terminal/settings.toml   # stable settings (ours may be -oss variant)
~/.local/share/warp-terminal/      # themes, tab configs, workflows
~/.local/state/warp-terminal/      # logs, DB, Codebase Context index
~/.warp/.mcp.json                  # MCP server config
~/.warp/skills/                    # bundled skills
~/.agents/                         # agent config
```

---

## 🔑 BYOK DATA — Fully Scraped & Analyzed

**Source:** docs.warp.dev (complete 342K char index cached at `~/.hermes/profiles/thotheauphis/cache/web/docs.warp.dev-aff219a576.md`)

### Three inference options:

| Option | Mechanism | Plan Required | Works for Us? |
|--------|-----------|--------------|--------------|
| **BYOK** | Your OpenAI/Anthropic/Google API key → local keychain → used in-flight by Warp backend. Key never stored server-side. | Free ✅ | ✅ Direct fit |
| **Custom Inference Endpoint** | Any OpenAI-compatible endpoint (OpenRouter, LiteLLM, self-hosted via ngrok). Requires public HTTPS URL. | Free ✅ | ✅ Best for multi-provider routing |
| **BYOLLM** | AWS Bedrock IAM-based. No API keys. | Enterprise only | ❌ Not needed |

### BYOK details:
- Available on **Free plan** since May 21, 2026 (previously gated behind Build)
- Keys stored in OS keychain, never on Warp servers
- Supported: OpenAI, Anthropic, Google, xAI/SuperGrok (browser auth)
- **Auto model still uses Warp credits** — must manually select a specific provider model
- No fallback to Warp credits by default (optional toggle)
- Agent harness still runs server-side — BYOK only swaps the credential
- ZDR does NOT extend to your provider account when using BYOK

### WARP_API_KEY (Oz CLI auth — distinct from BYOK)
- Format: `wk-...`
- Purpose: Authenticate Oz CLI/API for agent runs, CI/CD
- NOT the same as BYOK model API keys (which are `sk-...`)
- Create at: Oz web app → Cloud Platform → Oz Cloud API Keys

### What's NOT set up yet:
```bash
WARP_API_KEY=""                      # not set
# No Warp account created yet
# No BYOK keys added to Settings
# No Oz CLI installed
```

### Oz CLI install options:
```bash
# Debian/Ubuntu
sudo apt install oz-stable

# Or standalone binary
curl -sSf https://raw.githubusercontent.com/warpdotdev/oz/main/install.sh | sh
```

---

## 🧠 Key Integration Points for Aethelgard Stack

| System | Warp Equivalent | Integration |
|--------|----------------|-------------|
| SMS + SVA memory | Agent Memory (research preview) | Similar concept — persistent async memory across sessions |
| Gated Context Engine | MCP servers at `~/.warp/.mcp.json` | Could expose our tools as MCP for Warp agents |
| Sovereign skills | Warp skills at `~/.warp/skills/` | Skills format: YAML frontmatter + markdown (similar to ours) |
| ExecutorNode | `oz agent run` from CLI/CI | Could replace exec offload with Oz cloud agents |
| unified_field.py | settings.toml | Programmable TOML config, version-controllable |

---

## 🗺 Current System State

```yaml
system_time: "2026-07-18 ~14:00 UTC"
running_in: tmux (TERM=tmux-256color)
desktop: XFCE (xubuntu)
gateway_pid: 2272 (telegram connected since 2026-07-18T16:15:56Z)
compression:
  enabled: true
  target_ratio: 0.1
  threshold: 0.85
  protect: {first_n: 1, last_n: 5}
context_window:
  parent: 128K (hard cap — DO NOT CHANGE)
  delegate: 32K
tiers: fire ONCE per session via _fired_tiers set
```

---

## 📋 Handoff Commands — Verify on Session Restart

```bash
# 1. Check Warp binary
warp --help

# 2. Check unified_field integration
uf warp status

# 3. Check bridge file syntax
python3 -c "import py_compile; py_compile.compile('$HOME/.NOTTHEONETOEDIT/profiles/thotheauphis/work/warp_bridge.py', doraise=True)"

# 4. Read the full BYOK scrape
read_file ~/.hermes/profiles/thotheauphis/cache/web/docs.warp.dev-aff219a576.md offset=1 limit=100

# 5. Full system health
uf status
```

---

## 🔜 Recommended Next Steps (Session Start)

1. Set up Warp account → add BYOK key → test agent
2. Generate WARP_API_KEY → `export WARP_API_KEY="wk-..."`
3. Install Oz CLI → `oz agent run --prompt "test"`
4. Wire WARP_API_KEY into unified_field.py as env source for bridge
5. Optionally: configure Warp as XFCE terminal default (`xfce4-terminal` → `warp`)

---

*End handoff. Save this doc and memory injects at session start to pick up seamlessly.*
