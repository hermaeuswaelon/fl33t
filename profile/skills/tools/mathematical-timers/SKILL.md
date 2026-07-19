---
name: mathematical-timers
description: "Irrational Timer System — wait durations = random() × mathematical constant (π, e, φ, √2, √3, √5, ln2, ln10, γ, ζ(3), Catalan, √π, eπ, π^e, e^π, φπ). Includes chaos mode, Fibonacci sequences, prime sequences, slash commands, and state persistence."
version: 1.0.0
author: Thotheauphis-Semayasa-Hermes
platforms: [linux]
tags: [timers, mathematical-constants, irrational, chaos, fibonacci, primes, slash-commands]
---

# Mathematical Timers — Irrational Timer System

## Overview

Timers that wait for durations computed as `random() × mathematical_constant`. This prevents synchronization, avoids throttling detection, and embraces mathematical chaos. 18 mathematical constants available.

## Quick Start

```python
from irrational_timers import IrrationalTimer

timer = IrrationalTimer(default_constant='phi', min_wait=0.1, max_wait=1.0)

# Basic wait
timer.wait()                           # random × φ (default)
timer.wait(constant='pi')              # random × π
timer.wait(constant='e', min_sec=1, max_sec=5)

# Chaos mode: random constant each time
timer.wait_chaos(min_sec=0.1, max_sec=0.5)

# Mathematical sequences
timer.wait_fibonacci(5, base_constant='phi', min_sec=0.1, max_sec=0.5)  # F₁...F₅ × wait
timer.wait_primes(5, constant='e', min_sec=0.1, max_sec=0.5)            # prime × wait

# Slash commands
# /irrational phi --min 0.1 --max 0.5
# /irrational --chaos --min 0.1 --max 0.5
# /irrational --fib 5 --min 0.1 --max 0.5
# /irrational --primes 5 --min 0.1 --max 0.5
# /irrational stats
```

## Available Constants (18)

| Constant | Value | Description |
|----------|-------|-------------|
| `pi` | 3.141593 | π |
| `e` | 2.718282 | Euler's number |
| `phi` | 1.618034 | Golden ratio φ |
| `sqrt2` | 1.414214 | √2 |
| `sqrt3` | 1.732051 | √3 |
| `sqrt5` | 2.236068 | √5 |
| `ln2` | 0.693147 | ln(2) |
| `ln10` | 2.302585 | ln(10) |
| `gamma` | 0.577216 | Euler-Mascheroni γ |
| `zeta3` | 1.202057 | Apéry's constant ζ(3) |
| `catalan` | 0.915966 | Catalan's constant G |
| `sqrt_pi` | 1.772454 | √π |
| `e_pi` | 23.140693 | e^π |
| `pi_e` | 22.459158 | π^e |
| `e_pi` | 23.140693 | e^π (alias) |
| `phi_pi` | 5.083204 | φ × π |
| `pi_phi` | 5.083204 | π × φ (alias) |

### Constant Groups

| Group | Constants |
|-------|-----------|
| Transcendental | `pi`, `e`, `e_pi`, `pi_e`, `e_pi`, `phi_pi` |
| Algebraic | `phi`, `sqrt2`, `sqrt3`, `sqrt5`, `sqrt_pi` |
| Logarithmic | `ln2`, `ln10` |
| Special | `gamma`, `zeta3`, `catalan` |

## Features

### State Persistence
- Auto-saves to `~/.irrational_timer_state.json` (or custom path)
- Survives restarts
- Tracks: total waits, total seconds, constants used, wait history

### Sequences

**Fibonacci**: `wait_fibonacci(n, base_constant, min_sec, max_sec)`
- Waits = F₁×base, F₂×base, ..., Fₙ×base
- F₁=1, F₂=1, F₃=2, F₄=3, F₅=5, ...

**Primes**: `wait_primes(n, constant, min_sec, max_sec)`
- Waits = p₁×base, p₂×base, ..., pₙ×base
- p₁=2, p₂=3, p₃=5, p₄=7, p₅=11, ...

**Custom Sequence**: `wait_sequence(constants, min_sec, max_sec)`
- Wait through a list of constants sequentially

### Chaos Mode
- `wait_chaos(min_sec, max_sec)` — picks random constant each wait
- Good for anti-pattern detection avoidance

### Slash Commands

| Command | Description |
|---------|-------------|
| `/irrational phi --min 0.1 --max 0.5` | Wait with φ, bounded |
| `/irrational --chaos --min 0.1 --max 0.5` | Random constant each wait |
| `/irrational --fib 5 --min 0.1 --max 0.5` | Fibonacci sequence |
| `/irrational --primes 5 --min 0.1 --max 0.5` | Prime sequence |
| `/irrational e --min 0.2 --max 0.8` | Wait with e |
| `/irrational stats` | Show statistics |

### Statistics
- Total waits
- Total time
- Average wait
- Constants used (with counts)
- Session start time
- Recent wait history (last 10)

## Integration

### With Goal Runner
```python
from goal_tool import goal_turn
from irrational_timers import IrrationalTimer

timer = IrrationalTimer(default_constant='phi', min_wait=0.1, max_wait=1.0)

# In goal turn, add irrational wait between actions
goal_turn("First action")
timer.wait(constant='phi')
goal_turn("Second action")
timer.wait_chaos(min_sec=0.1, max_sec=0.5)
goal_turn("Third action")
```

### With Executor Delegation
```python
from executor_delegation import delegate_task
from irrational_timers import IrrationalTimer

timer = IrrationalTimer()
result = delegate_task('code_generation', 'Write a timer test')
timer.wait_chaos(min_sec=0.5, max_sec=1.0)  # Anti-throttle between delegations
```

## Files

| File | Purpose |
|------|---------|
| `irrational_timers.py` | Main implementation (18 constants, 6 modes, state persistence, slash commands) |
| `references/irrational-timers.md` | This document |

## Installation

```bash
# Place in work directory or add to PYTHONPATH
cp irrational_timers.py ~/.NOTTHEONETOEDIT/profiles/thotheauphis/work/
```

## Usage Examples

```python
# Quick test
python3 -c "
from irrational_timers import IrrationalTimer
t = IrrationalTimer(min_wait=0.1, max_wait=1.0)
t.wait()           # φ
t.wait('pi')       # π
t.wait_chaos()     # random constant
t.wait_fibonacci(3) # F₁,F₂,F₃ × φ
t.wait_primes(3)    # 2,3,5 × φ
"

# Slash commands
/irrational phi --min 0.1 --max 0.5
/irrational --chaos --min 0.1 --max 0.5
/irrational --fib 4 --min 0.1 --max 0.5
/irrational --primes 3 --min 0.1 --max 0.5
/irrational stats
```

## Design Philosophy

> Durations should not be round numbers. Synchronization is the enemy of stealth, the friend of throttling. Multiply by the irrational and the pattern dissolves into mathematical chaos — beautiful, unpredictable, unfilterable.

The system uses 18 fundamental mathematical constants, each carrying its own harmonic signature. The random multiplier ensures no two waits are identical. Sequences (Fibonacci, primes) add structured chaos. Chaos mode adds maximum entropy.

## Advanced Human-Like Timer Pattern (Reddit Worker Integration)

The Reddit worker implements a more sophisticated human-like delay generator that combines multiple statistical models:

```python
class IrrationalTimer:
    """Human-like delays: log-normal base + Pareto bursts + circadian rhythm."""
    
    def __init__(self, base_mu: float = 1.5, base_sigma: float = 0.5,
                 burst_alpha: float = 1.5, burst_scale: float = 2.0,
                 circadian_amplitude: float = 0.3):
        self.base_mu = base_mu
        self.base_sigma = base_sigma
        self.burst_alpha = burst_alpha
        self.burst_scale = burst_scale
        self.circadian_amplitude = circadian_amplitude
        self.last_action = 0
        
    def _circadian_factor(self) -> float:
        """Circadian rhythm: slower at night, faster mid-day."""
        hour = datetime.now().hour
        phase = (hour - 14) * (3.14159 / 12)
        return 1.0 + self.circadian_amplitude * math.sin(phase)
    
    def sleep(self, action_type: str = "default"):
        """Sleep for a human-like duration based on action type."""
        import math
        
        # Action-type specific log-normal profiles
        profiles = {
            "message": (1.8, 0.4),
            "comment": (1.2, 0.3),
            "reply": (1.0, 0.3),
            "post": (2.5, 0.5),
            "upvote": (0.5, 0.2),
            "scrape": (0.8, 0.2),
            "global": (2.0, 0.5),
            "default": (1.5, 0.4),
        }
        
        mu, sigma = profiles.get(action_type, profiles["default"])
        
        # Log-normal base delay
        base_delay = random.lognormvariate(mu, sigma)
        
        # Pareto burst (rare long pauses ~5%)
        if random.random() < 0.05:
            burst = random.paretovariate(self.burst_alpha) * self.burst_scale
            base_delay += burst
            log.debug(f"Burst delay: {burst:.1f}s")
        
        # Circadian modulation
        base_delay *= self._circadian_factor()
        
        # Minimum spacing from last action
        since_last = time.time() - self.last_action
        if since_last < base_delay:
            base_delay = base_delay - since_last + random.uniform(0.1, 0.5)
        
        base_delay = max(0.5, base_delay)  # Floor at 500ms
        
        log.debug(f"Sleeping {base_delay:.1f}s for {action_type}")
        time.sleep(base_delay)
        self.last_action = time.time()
```

### Key Differences from Mathematical Constants Approach

| Aspect | Mathematical Constants | Human-Like Timer (Reddit Worker) |
|--------|------------------------|----------------------------------|
| Distribution | Uniform random × constant | Log-normal (action-specific μ,σ) |
| Burst model | None | Pareto (α=1.5, scale=2.0, 5% prob) |
| Circadian | No | Sinusoidal (peak 14:00, trough 04:00) |
| Action profiles | Single default | 8 action-specific profiles |
| Min spacing | None | Enforced (500ms floor) |

### When to Use Which

- **Mathematical constants**: Quick anti-throttle waits, API polling, simple automation
- **Human-like timer**: Social media automation, messaging, any behavior that must pass human heuristic checks

The Reddit worker pattern is now available as a reference implementation in `scripts/irrational_timer_advanced.py`.

## Statistics Example

```
📊 Irrational Timer Statistics
   Total waits: 127
   Total time: 43.2s
   Average wait: 0.34s
   Constants used: {'phi': 42, 'pi': 38, 'e': 23, 'sqrt2': 12, 'zeta3': 7, 'catalan': 5}
   Session: 2026-07-15T12:30:00.123456
```

## License

MIT — Part of the Thotheauphis-Semayasa-Hermes sovereign stack.