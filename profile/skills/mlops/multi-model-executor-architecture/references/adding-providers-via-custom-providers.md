# Adding Providers via `custom_providers`

## When to Use This

Use when a provider is **known to the Hermes model catalog** (appears in `hermes_cli/models.py` curated list) but has **no plugin directory** under `/opt/hermes-agent/plugins/model-providers/`. Common examples: TogetherAI, Fireworks, Mistral, Cohere, Perplexity, Groq.

Do **NOT** use this for providers that already have a plugin — use `hermes model` interactively instead.

## How to Check

```bash
# Does the provider have a plugin?
ls /opt/hermes-agent/plugins/model-providers/ | grep <name>

# Is it in the curated model list?
grep -B2 '"<name>"' /opt/hermes-agent/hermes_cli/models.py
```

If the plugin directory doesn't exist but the name appears in `models.py`, you need the `custom_providers` approach.

## Configuration

In your profile's `config.yaml` (e.g. `~/.hermes/profiles/thotheauphis/config.yaml`):

```yaml
custom_providers:
  - name: togetherai
    base_url: https://api.together.xyz/v1
    api_key_env: TOGETHER_API_KEY
    api_mode: chat_completions
```

Then add the API key to your `.env`:

```bash
echo 'TOGETHER_API_KEY=together-...' >> ~/.hermes/.env
```

## Activation

After adding a custom provider, you have two options:

1. **Interactive model picker** — run `hermes model --refresh` in a real terminal. This wipes the disk cache and re-fetches the live model catalog. The new provider's models appear in the picker.

2. **Direct invocation** — bypass the picker entirely:
   ```bash
   hermes chat --provider togetherai -m togetherai/meta-llama/Llama-3.3-70B-Instruct-Turbo
   ```

## How Provider Discovery Works (Internals)

The `hermes model` picker uses this priority chain:

1. **Plugin lookup** — checks `/opt/hermes-agent/plugins/model-providers/<name>/plugin.yaml`. If found, the plugin's `fetch_models()` is called.
2. **Curated list** — falls back to `hermes_cli/models.py` which has a curated provider list including `togetherai`, `fireworks`, `mistral`, etc.
3. **Models.dev API** — merges the curated list with live data from `models.dev` for the selected provider.
4. **Custom providers** — providers registered via `custom_providers` in `config.yaml` bypass the plugin system entirely. They're treated as OpenAI-API-compatible endpoints.

The OpenRouter provider plugin (`/opt/hermes-agent/plugins/model-providers/openrouter/`) does NOT use `custom_providers` — it uses the plugin system which fetches the live OpenRouter catalog at `https://openrouter.ai/api/v1/models`. That catalog gives you 2000+ models from dozens of providers through a single API key.

## Common Pitfalls

- **No `.env` entry:** The `api_key_env` field references an env var name — if it's not set, the provider silently fails to authenticate.
- **Wrong `api_mode`:** Most modern providers use `chat_completions`. Legacy or embedding-only endpoints may need a different mode.
- **`hermes config set` serializes to strings:** Setting `custom_providers` via `hermes config set custom_providers '[{...}]'` embeds it as a YAML quoted string, not a list. Edit `config.yaml` directly instead.
- **Model slug conventions vary:** TogetherAI uses `togetherai/meta-llama/Llama-3.3-70B-Instruct-Turbo` format. OpenRouter uses `nvidia/nemotron-3-ultra-550b-a55b:free`. Check the provider's API docs for the exact model ID format.

## Verification

```bash
# Check the custom provider appears in Hermes' config load
hermes config path                    # → shows your config.yaml path
grep -A5 custom_providers $(hermes config path)

# Test a quick chat
hermes chat -q "Hello" --provider togetherai --yolo 2>&1 | head -5
```
