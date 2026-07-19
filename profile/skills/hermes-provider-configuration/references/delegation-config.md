# Delegation Provider Configuration

Delegate sub-agents inherit the parent model chain by default. To pin them to a specific model/provider:

```yaml
# In profile config.yaml (use `hermes config set`):
delegation:
  provider: <provider-name>     # matches the `name` field in custom_providers or a built-in provider
  model: <model-string>         # model ID as the provider expects it
```

## Commands
```bash
hermes config set delegation.provider <name>
hermes config set delegation.model "<model-id>"
```

## Notes
- Provider name must match exactly — for custom providers, use the `name` field value (e.g. `togetherai`)
- Max concurrent children defaults to 3; not currently configurable per-session
- Changes take effect on next session start
