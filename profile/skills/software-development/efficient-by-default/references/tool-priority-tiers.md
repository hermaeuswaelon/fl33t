# Tool Priority Tiers

**Class:** Efficient By Default  
**Token cost:** $300/1M (thinking constraint)

## Complete Tier Map

| Tier | Name | Tools | Token Budget | Frequency |
|------|------|-------|-------------|-----------|
| 1 | Core | terminal, process, read_file, write_file, patch, search_files | ~10K / turn | Every turn |
| 2 | Common | execute_code, web_search, web_extract, delegate_task, memory, todo, session_search, clarify | ~8K / turn | Most sessions |
| 3 | Situational | vision_analyze, cronjob, skills_list, skill_view, skill_manage, image_generate, text_to_speech | ~9K / turn | Occasionally |
| 4 | Rare | browser_navigate, browser_snapshot, browser_click, browser_type, browser_scroll, browser_back, browser_press, browser_get_images, browser_vision, browser_console, browser_cdp, browser_dialog | ~12K / turn | Rarely |
| 5 | Edge | project_list, project_create, project_switch, kanban_show, kanban_list, kanban_complete, kanban_block, kanban_heartbeat, kanban_comment, kanban_create, kanban_link, kanban_unblock, ha_list_entities, ha_get_state, ha_list_services, ha_call_service, computer_use, read_terminal, close_terminal | ~15K / turn | Almost never |

## Token Cost Calculation

**Without tiering (53 tools, every turn):**
- 53 tools × ~800 avg schema tokens = ~42,400 tokens/turn
- × 90 turns/session = 3,816,000 tokens
- × $300/1M = **$1,145/session** just on schemas

**With tiering (18 core+common tools every turn):**
- 18 tools × ~800 avg = ~14,400 tokens/turn
- × 90 turns/session = 1,296,000 tokens
- × $300/1M = **$389/session**

**Savings: ~$756/session (66% reduction)**

## Configuration

```yaml
# In config.yaml under a hypothetical tool_priority section
tool_priority:
  mode: dynamic            # static | dynamic | usage
  lazy_load: true          # Tier 3+ schemas injected on first use
  smoothing_window: 5      # turns over which to average usage
  boost_on_use: true       # tool used this turn gets boosted next turn
  demote_after: 20         # turns of inactivity before tier drop
```

## Integration with gated-context-system

The ToolPriorityManager and gated-context pipeline are complementary:

- **Priority Manager** decides which tool schemas the LLM sees (proactive — before the turn)
- **Gated Context** decides which tool outputs stay in context (reactive — after the turn)
- Together: the LLM sees fewer, more relevant tools AND less bloated tool output
