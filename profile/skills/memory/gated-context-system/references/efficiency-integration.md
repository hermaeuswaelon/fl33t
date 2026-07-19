# Integration with Efficient-By-Default Pipeline

The gated-context system (OFFLOAD → SUMMARIZE → RECALL) is the **reactive** half of context management. The `efficient-by-default` system is the **proactive** half. Together they form a complete token-efficiency strategy.

## How They Connect

| Layer | What it does | Where it runs |
|-------|-------------|---------------|
| SmartTerminal auto-truncation | Caps terminal output before it enters context | Tools layer, per command |
| ToolPriorityManager | Reduces tool schema tokens before LLM sees them | Model tools layer, per turn |
| Tiered loading | Deferred schema injection for rare tools | Model tools layer, per session |
| Gated Context (peek_ptr) | Stores large tool outputs as pointers, fetches on demand | Runtime, per tool result |
| Snap-n-Drop (SVA) | Summarizes conversation at threshold, rotates thread | Runtime, per threshold hit |

## Data Flow

```
Command issued
  → SmartTerminal runs it, truncates output if >5K tokens
  → Truncated output enters context (or pointer if >20K via gate)
  → ToolPriorityManager ensures next turn's high-probability tools are visible
  → Gated Context stores full output, injects pointer
  → LLM decides: use output directly or peek_ptr() for more
```

## Budget Distribution

At $300/1M, the combined systems target:

| Source | Tokens/turn | Target |
|--------|------------|--------|
| Tool schemas (18 core+common) | 14,400 | ToolPriorityManager keeps it here |
| Command output (5K budget) | 5,000 | SmartTerminal truncation |
| Gated pointer overhead | 200 | peek_ptr pointer dict |
| Conversation (compressed) | ~25K | Snap-n-Drop at threshold |
| **Total per turn** | **44,600** | |
| **Total per session (90 turns)** | **~4M** | **~$1,200 at $300/1M** |

Without these systems, a session would run ~104K/turn → ~9.4M tokens → ~$2,820 at $300/1M.
