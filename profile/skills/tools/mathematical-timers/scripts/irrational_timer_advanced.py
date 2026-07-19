#!/usr/bin/env python3
"""
Advanced Human-Like Irrational Timer
=====================================
Combines log-normal base delays, Pareto bursts, and circadian rhythm modulation
with action-type specific profiles.

Reference implementation from the Reddit Worker (Bromium Portal project).
"""

import math
import random
import time
import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

log = logging.getLogger("irrational_timer_advanced")


@dataclass
class TimerProfile:
    """Log-normal parameters for a specific action type."""
    mu: float
    sigma: float


# Action-type specific log-normal profiles (μ, σ for lognormvariate)
ACTION_PROFILES = {
    "message": TimerProfile(1.8, 0.4),      # Sending PMs — slow, careful
    "comment": TimerProfile(1.2, 0.3),      # Public comments — moderate
    "reply": TimerProfile(1.0, 0.3),        # Replies — slightly faster
    "post": TimerProfile(2.5, 0.5),         # Creating posts — slowest
    "upvote": TimerProfile(0.5, 0.2),       # Quick reactions
    "scrape": TimerProfile(0.8, 0.2),       # Reading — fast
    "global": TimerProfile(2.0, 0.5),       # Between actions
    "default": TimerProfile(1.5, 0.4),
}


class IrrationalTimerAdvanced:
    """
    Human-like delay generator combining:
    - Log-normal distribution (action-specific profiles)
    - Pareto-distributed burst pauses (rare long delays)
    - Circadian rhythm modulation (time-of-day awareness)
    - Minimum action spacing enforcement
    """
    
    def __init__(
        self,
        burst_alpha: float = 1.5,
        burst_scale: float = 2.0,
        burst_probability: float = 0.05,
        circadian_amplitude: float = 0.3,
        min_wait: float = 0.5,
        profiles: Optional[dict] = None,
    ):
        self.burst_alpha = burst_alpha
        self.burst_scale = burst_scale
        self.burst_probability = burst_probability
        self.circadian_amplitude = circadian_amplitude
        self.min_wait = min_wait
        self.profiles = profiles or ACTION_PROFILES
        self.last_action = 0.0
        
    def _circadian_factor(self) -> float:
        """Circadian rhythm: peak at 14:00 (2pm), trough at 04:00."""
        hour = datetime.now().hour
        phase = (hour - 14) * (math.pi / 12)
        return 1.0 + self.circadian_amplitude * math.sin(phase)
    
    def sleep(self, action_type: str = "default") -> float:
        """
        Sleep for a human-like duration.
        
        Args:
            action_type: One of 'message', 'comment', 'reply', 'post', 
                        'upvote', 'scrape', 'global', 'default'
        
        Returns:
            Actual seconds slept
        """
        profile = self.profiles.get(action_type, self.profiles["default"])
        
        # Log-normal base delay
        base_delay = random.lognormvariate(profile.mu, profile.sigma)
        
        # Pareto burst (rare long pauses)
        if random.random() < self.burst_probability:
            burst = random.paretovariate(self.burst_alpha) * self.burst_scale
            base_delay += burst
            log.debug(f"IrrationalTimer: Pareto burst {burst:.1f}s added")
        
        # Circadian modulation
        base_delay *= self._circadian_factor()
        
        # Minimum spacing from last action
        since_last = time.time() - self.last_action
        if since_last < base_delay:
            base_delay = base_delay - since_last + random.uniform(0.1, 0.5)
        
        # Floor
        base_delay = max(self.min_wait, base_delay)
        
        log.debug(f"IrrationalTimer: Sleeping {base_delay:.1f}s for {action_type}")
        time.sleep(base_delay)
        self.last_action = time.time()
        
        return base_delay
    
    def get_delay(self, action_type: str = "default") -> float:
        """Get a delay value without sleeping (for planning/analysis)."""
        profile = self.profiles.get(action_type, self.profiles["default"])
        base_delay = random.lognormvariate(profile.mu, profile.sigma)
        
        if random.random() < self.burst_probability:
            base_delay += random.paretovariate(self.burst_alpha) * self.burst_scale
            
        base_delay *= self._circadian_factor()
        base_delay = max(self.min_wait, base_delay)
        return base_delay
    
    def stats(self, n_samples: int = 10000) -> dict:
        """Generate statistics for all action types."""
        results = {}
        for action_type in self.profiles:
            samples = [self.get_delay(action_type) for _ in range(n_samples)]
            results[action_type] = {
                "mean": sum(samples) / len(samples),
                "median": sorted(samples)[len(samples)//2],
                "min": min(samples),
                "max": max(samples),
                "p95": sorted(samples)[int(len(samples) * 0.95)],
            }
        return results


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")
    
    timer = IrrationalTimerAdvanced()
    
    print("=== Single Wait Demo ===")
    for action in ["message", "comment", "post", "upvote", "scrape"]:
        print(f"{action:10s}: ", end="")
        d = timer.get_delay(action)
        print(f"{d:.2f}s")
    
    print("\n=== Statistics (10000 samples each) ===")
    stats = timer.stats(10000)
    for action, s in stats.items():
        print(f"{action:10s}: mean={s['mean']:.2f}s  median={s['median']:.2f}s  "
              f"p95={s['p95']:.2f}s  range={s['min']:.2f}-{s['max']:.2f}s")
    
    print("\n=== Circadian Factor (24h cycle) ===")
    for hour in range(0, 24, 2):
        dt = datetime(2026, 1, 1, hour, 0)
        # Temporarily override datetime.now for demo
        original_now = datetime.now
        datetime.now = lambda: dt
        factor = timer._circadian_factor()
        print(f"  {hour:02d}:00 -> {factor:.2f}x")
        datetime.now = original_now