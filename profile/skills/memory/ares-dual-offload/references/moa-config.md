# Triple-Executor MOA Config
# Deployed: 2026-07-15
# Previous: had Nemotron 3 Super + DeepSeek Reasoner as additional refs
# Changed to: Ultra + Nano only (user preference: "both are free, make MOA just those 2")

moa:
  presets:
    default:
      reference_models:
        - provider: openrouter
          model: nvidia/nemotron-3-ultra-550b-a55b:free
        - provider: openrouter
          model: nvidia/nemotron-3-nano-30b-a3b:free
      aggregator:
        provider: deepseek
        model: deepseek-reasoner
      fanout: per_iteration
  reference_models:
    - provider: openrouter
      model: nvidia/nemotron-3-ultra-550b-a55b:free
    - provider: openrouter
      model: nvidia/nemotron-3-nano-30b-a3b:free
  aggregator:
    provider: deepseek
    model: deepseek-reasoner
  max_tokens: 4096
  fanout: per_iteration
  enabled: true

# Usage:
#   /moa <prompt>  — runs prompt through both executors, aggregates via prime
#
# To switch to a specific executor without MOA:
#   hermes chat -q "<prompt>" --provider openrouter \
#     -m nvidia/nemotron-3-nano-30b-a3b:free          # Nano (fast)
#   hermes chat -q "<prompt>" --provider openrouter \
#     -m nvidia/nemotron-3-ultra-550b-a55b:free        # Ultra (deep)
#
# To use executors via delegate_task:
#   delegate_task(goal=..., model={"provider": "openrouter",
#                   "model": "nvidia/nemotron-3-nano-30b-a3b:free"})

# X11/computer-use note:
# The executor tooling (xdotool, cua-driver) works for both executors.
# Type /moa "click at 500,500" and both executors will analyze the result.
