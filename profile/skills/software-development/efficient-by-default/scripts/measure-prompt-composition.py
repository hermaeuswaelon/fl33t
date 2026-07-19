#!/usr/bin/env python3
"""Quick measurement of current system prompt composition."""
import json, subprocess, sys

result = subprocess.run(
    ["hermes", "prompt-size", "--json"],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)

sys_prompt = data["system_prompt"]
skills = data["skills_index"]
memory = data["memory"]
profile = data["user_profile"]
tools = data["tools"]
sections = data.get("sections", [])

print("=== SYSTEM PROMPT COMPOSITION ===")
print(f"Total:         {sys_prompt['chars']:>7} chars  ({sys_prompt['bytes']:>7} bytes)")
print(f"Skills index:  {skills['chars']:>7} chars  ({skills['bytes']:>7} bytes)  ({100*skills['bytes']/sys_prompt['bytes']:.1f}%)")
print(f"Memory:        {memory['chars']:>7} chars  ({memory['bytes']:>7} bytes)")
print(f"Profile:       {profile['chars']:>7} chars  ({profile['bytes']:>7} bytes)")
print(f"Tools:         {tools['count']:>7} tools  ({tools['json_bytes']:>7} bytes)")

for label, chars, bytes_ in sections:
    print(f"Section '{label}': {chars:>7} chars  ({bytes_:>7} bytes)")

total_overhead = sys_prompt['bytes'] + tools['json_bytes']
print(f"\nOverhead per turn: ~{total_overhead} bytes ≈ ~{total_overhead//4} tokens")
print(f"(vs DeepSeek 128K cap = 131072 tokens)")
