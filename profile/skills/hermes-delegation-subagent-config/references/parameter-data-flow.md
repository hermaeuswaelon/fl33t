# Parameter Data Flow in Hermes Delegation

## Full Trace: Config → Child Agent API Call

```
config.yaml
  └─ delegation.request_overrides = {temperature: 0.1, ...}
       │
       ▼
_load_config()  [tools/delegate_tool.py:3155]
  └─ returns delegation sub-dict
       │
       ▼
_build_child_agent()  [tools/delegate_tool.py:1044]
  └─ delegation_cfg = _load_config()
  └─ _deleg_req_overrides = delegation_cfg.get("request_overrides", {})
  └─ MERGE with override_request_overrides (from _resolve_delegation_credentials)
  └─ pass as request_overrides to AIAgent(...)
       │
       ▼
init_agent()  [agent/agent_init.py]
  └─ agent.request_overrides = dict(request_overrides or {})
       │
       ▼
build_kwargs()  [agent/transports/chat_completions.py]
  └─ api_kwargs.update(overrides)   ← line 507
       │
       ▼
OpenRouter API call
  └─ temperature, top_p, top_k, penalties sent in request body
```

## Credential Resolution Path

```
_resolve_delegation_credentials(cfg, parent_agent)
  └─ Reads: cfg.get("model"), cfg.get("provider"), cfg.get("base_url"),
     cfg.get("api_key"), cfg.get("api_mode")
  └─ When delegation.provider is set (e.g. "openrouter"):
       → resolve_runtime_provider(requested="openrouter")
       → returns: provider, api_mode, base_url, api_key
       → request_overrides from runtime is EMPTY for openrouter
  └─ Returns: {"model", "provider", "base_url", "api_key",
               "api_mode", "request_overrides", "max_output_tokens", ...}
```

## Key Insight

The `_resolve_delegation_credentials` function returns `request_overrides` from the *provider runtime* (which is empty for OpenRouter). The patch adds a SECOND source — `delegation.request_overrides` from config — and merges them with the runtime overrides winning on conflict only when the same key appears in both.
