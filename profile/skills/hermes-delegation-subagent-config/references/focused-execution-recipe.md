# Focused Execution Parameter Recipe

## Use Case
When you need a subagent/parallel worker to produce deterministic, concise,
focused output — not creative exploration.

## The Recipe

```yaml
delegation:
  model: qwen/qwen-2.5-coder-32b-instruct   # or any instruct model
  provider: openrouter
  request_overrides:
    temperature: 0.1          # near-deterministic
    top_k: 20                 # restrict token pool
    top_p: 0.1                # narrow nucleus sampling
    frequency_penalty: 0.5    # mild repetition dampening
    presence_penalty: 0.4     # slight topic diversity
    repetition_penalty: 1.2   # stronger n-gram penalty
    max_tokens: 500           # output budget
```

## Reasoning Budget

**Does NOT apply** to Qwen 2.5 Coder or most instruct models. The `reasoning_budget`
parameter is specific to reasoning models (DeepSeek-R1, etc.) that allocate
explicit thinking tokens. For Qwen, this is silently ignored.

## When to Adjust

| Signal | Parameter | Direction |
|--------|-----------|-----------|
| Output too repetitive | frequency_penalty or repetition_penalty | Raise by 0.1–0.3 |
| Output too random/creative | temperature or top_p | Lower |
| Output too short | max_tokens | Raise |
| Missing important topics | presence_penalty | Raise slightly |
| Output incoherent/truncated | max_tokens or temperature | Raise max_tokens, lower temperature |
