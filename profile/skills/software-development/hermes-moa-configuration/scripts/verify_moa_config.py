#!/usr/bin/env python3
"""
MOA Configuration Verification Script
=====================================
Verifies that the MOA preset loads correctly with all per-model parameters.
"""

import sys
import json

# Add Hermes to path
sys.path.insert(0, "/opt/hermes-agent")

from hermes_cli.config import load_config
from hermes_cli.moa_config import resolve_moa_preset


def main():
    print("=" * 60)
    print("MOA Configuration Verification")
    print("=" * 60)
    
    cfg = load_config()
    moa_cfg = cfg.get("moa") or {}
    
    # Check MOA is enabled
    enabled = moa_cfg.get("enabled", False)
    print(f"\nMOA Enabled: {enabled}")
    if not enabled:
        print("⚠️  MOA is disabled. Run: hermes config set moa.enabled true")
        return 1
    
    # Check default preset
    preset_name = moa_cfg.get("default_preset", "default")
    print(f"Default Preset: {preset_name}")
    
    # Resolve preset
    preset = resolve_moa_preset(moa_cfg, preset_name)
    
    print(f"\n{'='*60}")
    print(f"PRESET: {preset_name}")
    print(f"{'='*60}")
    
    # Check reference models
    refs = preset.get("reference_models", [])
    print(f"\nReference Models: {len(refs)}")
    
    required_params = [
        "provider", "model", "temperature", "top_p", "top_k",
        "frequency_penalty", "presence_penalty", "max_tokens",
        "reasoning_budget", "context_limit"
    ]
    
    all_ok = True
    for i, ref in enumerate(refs):
        print(f"\n  Reference Model {i+1}:")
        print(f"    Provider: {ref.get('provider')}")
        print(f"    Model: {ref.get('model')}")
        
        for param in required_params:
            value = ref.get(param)
            status = "✓" if value is not None else "✗ MISSING"
            if value is None:
                all_ok = False
            print(f"    {param}: {value} {status}")
        
        delay = ref.get("delay_seconds", 0)
        print(f"    delay_seconds: {delay} {'✓' if delay >= 0 else '✗'}")
    
    # Check aggregator
    agg = preset.get("aggregator_model", {})
    print(f"\nAggregator Model:")
    print(f"  Provider: {agg.get('provider')}")
    print(f"  Model: {agg.get('model')}")
    
    agg_required = required_params + ["delay_seconds"]
    for param in agg_required:
        value = agg.get(param)
        status = "✓" if value is not None else "✗ MISSING"
        if value is None:
            all_ok = False
        print(f"  {param}: {value} {status}")
    
    # Summary
    print(f"\n{'='*60}")
    if all_ok:
        print("✅ ALL CHECKS PASSED — MOA configuration is complete")
        return 0
    else:
        print("❌ SOME PARAMETERS MISSING — check config.yaml")
        return 1


if __name__ == "__main__":
    sys.exit(main())