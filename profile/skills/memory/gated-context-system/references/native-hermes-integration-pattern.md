# Adding Tools, Slash Commands, and CLI Flags to Hermes Source

## Tool Registration (Built-in Tools)

Tools in `/opt/hermes-agent/tools/` are auto-discovered at session start via
`discover_builtin_tools()` in `tools/registry.py`.

### Requirements for auto-discovery

1. **File must be in `tools/` directory** — named `tools/<name>_tool.py`
2. **Top-level `registry.register()` calls** — the AST scanner (`_module_registers_tools`)
   checks for `Expr > Call > Attribute(attr='register') > Name(id='registry')` at the
   **module body level** (not inside a function or for-loop)
3. **Must pass text prefilter** — source must contain both `"registry"` and `"register"` strings

### Registration pattern (top-level)

```python
from tools.registry import registry
from pathlib import Path

_FLEET_MODULES = Path.home() / "projects" / "aethelgard" / "fleet" / "modules"

def _fleet_available() -> bool:
    return _FLEET_MODULES.exists()

# Schema dict
MY_TOOL_SCHEMA = {
    "name": "my_tool",
    "description": "...",
    "parameters": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."},
        },
        "required": ["param"],
    },
}

# Handler function
def handle_my_tool(args: dict, **kw) -> str:
    return json.dumps({"result": "..."})

# TOP-LEVEL registration (not inside a function!)
registry.register(
    name="my_tool",
    toolset="context_engine",    # or any existing toolset name
    schema=MY_TOOL_SCHEMA,
    handler=handle_my_tool,
    check_fn=_fleet_available,   # gated — tool only appears when True
    description="What this tool does",
)
```

### Wiring into core toolsets

Add to `_HERMES_CORE_TOOLS` in `/opt/hermes-agent/toolsets.py` to make the tool
available on every platform (CLI, TUI, Telegram, Discord, cron, etc.):

```python
_HERMES_CORE_TOOLS = [
    # ... existing tools ...
    "peek_ptr", "gate_status", "gate_injectable", "recall",  # add yours here
]
```

Alternatively, add to a specific platform toolset's `includes` or `tools` list.

---

## Slash Commands

### 1. Register in COMMAND_REGISTRY

File: `/opt/hermes-agent/hermes_cli/commands.py`

```python
CommandDef("uf", "Unified Field system health, recall, memorize, and checkpoint commands",
           "Tools & Skills", cli_only=True,
           args_hint="[status|recall|memorize|checkpoint|wf|offload|warp]",
           subcommands=("status", "recall", "memorize", "checkpoint",
                        "wf", "offload", "warp", "sync")),
```

Parameters:
- Positional: name, description, category
- `cli_only=True` — only available in CLI/TUI, not gateway
- `gateway_only=True` — only available on messaging platforms
- `args_hint` — shown in help
- `subcommands` — enables tab-completion for subcommands
- `aliases=("short",)` — alternative names

### 2. Add handler method to CLICommandsMixin

File: `/opt/hermes-agent/hermes_cli/cli_commands_mixin.py`

```python
def _handle_uf_command(self, cmd_original: str) -> None:
    """Handle /uf — Unified Field system commands."""
    import subprocess, shutil
    from cli import _cprint, _DIM, _RST

    uf_bin = shutil.which("uf")
    if not uf_bin:
        _cprint("  ✗ uf CLI not found in PATH.")
        return

    parts = cmd_original.split(maxsplit=1)
    args = parts[1] if len(parts) > 1 else "status"

    try:
        result = subprocess.run(
            [uf_bin] + args.split(),
            capture_output=True, text=True, timeout=15
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            _cprint(f"  ✗ uf exited with code {result.returncode}")
    except FileNotFoundError:
        _cprint("  ✗ uf CLI not found. Check PATH.")
```

### 3. Add dispatch entry to process_command()

File: `/opt/hermes-agent/cli.py`

The `process_command()` method has an `elif canonical == "name":` chain. Add:

```python
elif canonical == "uf":
    self._handle_uf_command(cmd_original)
elif canonical == "grindmode":
    self._handle_grindmode_command(cmd_original)
```

The resolver (`resolve_command`) canonicalizes aliases, so the `elif` uses the
canonical name from `CommandDef`, not the alias.

---

## CLI Flags

### 1. Add to both parsers

File: `/opt/hermes-agent/hermes_cli/_parser.py`

Add to `build_top_level_parser()` for the top-level `hermes` command:

```python
_inherited_flag(
    parser,
    "--grind",
    action="store_true",
    default=False,
    help="Grind mode: bare execution engine, no scaffolding, no memory, YOLO. "
         "Sets sovereign prompt to grindmode-prompt.txt, implies --ignore-rules and --yolo",
)
```

Add to the chat subparser for `hermes chat --grind`:

```python
_inherited_flag(
    chat_parser,
    "--grind",
    action="store_true",
    default=argparse.SUPPRESS,
    help="...",
)
```

`_inherited_flag()` is equivalent to `parser.add_argument()` plus tagging
the action with `inherit_on_relaunch = True` so the flag survives CLI
re-execution (e.g. after session browse picks a session).

### 2. Wire env var setting in main.py

File: `/opt/hermes-agent/hermes_cli/main.py`

Create a function near `_apply_safe_mode()`:

```python
def _apply_grind_mode(args) -> None:
    """Apply --grind: bare execution mode with sovereign prompt bypass."""
    if not getattr(args, "grind", False):
        return
    os.environ["HERMES_YOLO_MODE"] = "1"
    os.environ["HERMES_IGNORE_RULES"] = "1"
    grind_prompt = os.environ.get(
        "HERMES_GRIND_PROMPT",
        os.path.expanduser("~/.hermes/profiles/thotheauphis/grindmode-prompt.txt")
    )
    if os.path.exists(grind_prompt):
        os.environ["HERMES_SOVEREIGN_PROMPT"] = grind_prompt
```

Call it alongside `_apply_safe_mode()` at each call site (currently 2 call sites):
```python
_apply_safe_mode(args)
_apply_grind_mode(args)
```

---

## Verification Checklist

After adding new tools/commands/flags:

```bash
# Smoke imports
python3 -c "from tools.registry import discover_builtin_tools; print(discover_builtin_tools())"

# Run command registration tests
python3 -m pytest tests/hermes_cli/test_commands.py -v --tb=short

# Run tool discovery tests
python3 -m pytest tests/tools/test_skills_tool_discovery_cache.py -v --tb=short

# Verify flag parses
python3 -c "from hermes_cli._parser import build_top_level_parser; p,_,_=build_top_level_parser(); p.parse_args(['--grind'])"

# Verify handler exists
python3 -c "from hermes_cli.cli_commands_mixin import CLICommandsMixin; assert hasattr(CLICommandsMixin, '_handle_uf_command')"
```
