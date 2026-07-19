"""Configurable tool-output truncation limits.

Ported from anomalyco/opencode PR #23770 (``feat(truncate): allow
configuring tool output truncation limits``).

OpenCode hardcoded ``MAX_LINES = 2000`` and ``MAX_BYTES = 50 * 1024``
as tool-output truncation thresholds. Hermes-agent had the same
hardcoded constants in two places:

* ``tools/terminal_tool.py`` — ``MAX_OUTPUT_CHARS = 50000`` (terminal
  stdout/stderr cap)
* ``tools/file_operations.py`` — ``MAX_LINES = 2000`` /
  ``MAX_LINE_LENGTH = 2000`` (file read caps)

This module centralises those limits and makes them configurable via
``config.yaml`` under the ``tool_output`` key. Defaults match the
original hardcoded values, so adding this module is behaviour-preserving
for users who don't set ``tool_output`` in config.yaml.
"""

import os
from typing import Dict, Optional

from hermes_constants import get_hermes_home

# ─── Defaults (match original hardcoded values) ───
DEFAULT_MAX_BYTES = 50_000       # terminal_tool.MAX_OUTPUT_CHARS
DEFAULT_MAX_LINES = 2000         # file_operations.MAX_LINES
DEFAULT_MAX_LINE_LENGTH = 2000   # file_operations.MAX_LINE_LENGTH

# ─── Module-level cache — populated on first call ───
_cached_limits: Optional[Dict[str, int]] = None


def _load_config_limits() -> Dict[str, int]:
    """Read tool_output limits from config.yaml."""
    global _cached_limits
    if _cached_limits is not None:
        return _cached_limits

    limits = {
        "max_bytes": DEFAULT_MAX_BYTES,
        "max_lines": DEFAULT_MAX_LINES,
        "max_line_length": DEFAULT_MAX_LINE_LENGTH,
    }

    try:
        import yaml
        config_path = get_hermes_home() / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            tool_output = config.get("tool_output")
            if isinstance(tool_output, dict):
                for key in ("max_bytes", "max_lines", "max_line_length"):
                    if key in tool_output and isinstance(tool_output[key], int):
                        limits[key] = tool_output[key]
    except Exception:
        pass  # fallback to defaults on any config error

    _cached_limits = limits
    return limits


def get_tool_output_limits() -> Dict[str, int]:
    """Return current tool-output limits (cached after first load)."""
    return _load_config_limits()


def get_max_bytes() -> int:
    """Terminal stdout/stderr character cap."""
    return get_tool_output_limits()["max_bytes"]


def get_max_lines() -> int:
    """File read line cap."""
    return get_tool_output_limits()["max_lines"]


def get_max_line_length() -> int:
    """Per-line character cap for file reads."""
    return get_tool_output_limits()["max_line_length"]