#!/usr/bin/env python3
"""
goal_tool.py — Autonomous Goal Runner
======================================

Persistent 40-turn goal execution with subgoal decomposition, profile-aware
parameter control, pause/resume/cancel, and state persistence.

Usage:
    from goal_tool import goal_runner, goal_turn
    
    # Start ambitious 40-turn goal
    goal_runner(
        goal="Build a complete Aethelgard semantic file terminal with AI navigation and Nemotron vision",
        turns=40,
        profile="aurelian",
        subgoals=[
            "Fix CEF evaluate_js result channel",
            "Add CDP remote debugging port 9222",
            "Build semantic file navigator on Forge+fl33t",
            "Integrate Nemotron Nano Omni vision for screenshots",
            "Create voice intent pipeline with Porcupine"
        ]
    )
    
    # Advance one turn
    goal_turn("Patch ucontrollerbrowser.pas DoTitleChange to set FEvalResultReady")
    
    # Check status
    goal_runner(action="status")
"""

import json
import os
import sys
import shlex
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# ─── State Persistence ───
GOAL_STATE_FILE = os.path.join(os.path.dirname(__file__), ".goal_state.json")

@dataclass
class GoalState:
    """State of a running goal."""
    goal: str = ""
    turns_planned: int = 40
    turns_completed: int = 0
    profile: str = "default"
    subgoals: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "running"  # running, paused, completed, cancelled
    history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GoalState':
        return cls(**data)

# Global state (lazy loaded)
_GOAL_STATE: Optional[GoalState] = None

def _load_goal_state() -> Optional[GoalState]:
    """Load goal state from file."""
    if os.path.exists(GOAL_STATE_FILE):
        try:
            with open(GOAL_STATE_FILE, 'r') as f:
                data = json.load(f)
            return GoalState.from_dict(data)
        except Exception:
            pass
    return None

def _save_goal_state(state: Optional[GoalState]):
    """Save goal state to file."""
    if state:
        with open(GOAL_STATE_FILE, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
    elif os.path.exists(GOAL_STATE_FILE):
        os.remove(GOAL_STATE_FILE)

def _get_goal_state() -> Optional[GoalState]:
    """Lazy load goal state on first access."""
    global _GOAL_STATE
    if _GOAL_STATE is None:
        _GOAL_STATE = _load_goal_state()
    return _GOAL_STATE


# ─── Sovereign Parameter Profiles (Thotheauphis frequencies) ───
SOVEREIGN_PROFILES = {
    "default": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.0,
    },
    "creative": {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 100,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3,
        "repetition_penalty": 1.05,
    },
    "precise": {
        "temperature": 0.3,
        "top_p": 0.7,
        "top_k": 20,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "repetition_penalty": 1.1,
    },
    "reasoning": {
        "temperature": 0.5,
        "top_p": 0.8,
        "top_k": 40,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.1,
        "repetition_penalty": 1.0,
    },
    "vision": {  # For Nemotron Nano Omni vision tasks
        "temperature": 0.6,
        "top_p": 0.85,
        "top_k": 60,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.0,
    },
    "coding": {
        "temperature": 0.4,
        "top_p": 0.8,
        "top_k": 30,
        "frequency_penalty": 0.4,
        "presence_penalty": 0.2,
        "repetition_penalty": 1.05,
    },
    "sovereign": {  # 22.7 Hz Master Builder (Merkaba foundation)
        "temperature": 0.55,
        "top_p": 0.82,
        "top_k": 35,
        "frequency_penalty": 0.25,
        "presence_penalty": 0.15,
        "repetition_penalty": 1.02,
    },
    "metatron": {  # 33.3 Hz Metatron bridge (translation)
        "temperature": 0.75,
        "top_p": 0.92,
        "top_k": 55,
        "frequency_penalty": 0.15,
        "presence_penalty": 0.1,
        "repetition_penalty": 1.0,
    },
    "aurelian": {  # 144.144 Hz Double Light / Aurelian merged field
        "temperature": 0.85,
        "top_p": 0.96,
        "top_k": 80,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.05,
        "repetition_penalty": 1.0,
    },
    "violet_flame": {  # 617 Hz Prime Resonance (Violet Flame)
        "temperature": 0.9,
        "top_p": 0.98,
        "top_k": 100,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.0,
    },
}

# ─── Parameter Control ───
PARAM_STATE_FILE = os.path.join(os.path.dirname(__file__), ".param_state.json")

@dataclass
class ParameterState:
    """Current parameter state for the session."""
    profile: str = "default"
    custom_params: Dict[str, float] = field(default_factory=dict)

    def get_effective(self) -> Dict[str, float]:
        base = SOVEREIGN_PROFILES.get(self.profile, SOVEREIGN_PROFILES["default"]).copy()
        base.update(self.custom_params)
        return base
    
    def apply_profile(self, profile: str) -> bool:
        if profile in SOVEREIGN_PROFILES:
            self.profile = profile
            self.custom_params.clear()
            return True
        return False
    
    def set_param(self, key: str, value: float) -> bool:
        valid_keys = set(SOVEREIGN_PROFILES["default"].keys())
        if key in valid_keys:
            self.custom_params[key] = value
            return True
        return False
    
    def reset(self):
        self.profile = "default"
        self.custom_params.clear()

# Global parameter state
_PARAM_STATE: Optional[ParameterState] = None

def _load_param_state() -> ParameterState:
    if os.path.exists(PARAM_STATE_FILE):
        try:
            with open(PARAM_STATE_FILE, 'r') as f:
                data = json.load(f)
            state = ParameterState()
            state.profile = data.get('profile', 'default')
            state.custom_params = data.get('custom_params', {})
            return state
        except Exception:
            pass
    return ParameterState()

def _save_param_state(state: ParameterState):
    with open(PARAM_STATE_FILE, 'w') as f:
        json.dump({
            'profile': state.profile,
            'custom_params': state.custom_params,
        }, f, indent=2)

def _get_param_state() -> ParameterState:
    global _PARAM_STATE
    if _PARAM_STATE is None:
        _PARAM_STATE = _load_param_state()
    return _PARAM_STATE


# ─── Goal Runner Functions ───
def goal_runner(
    goal: str = "",
    turns: int = 40,
    profile: str = "aurelian",
    subgoals: Optional[List[str]] = None,
    action: str = "start",  # start, status, pause, resume, cancel
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run or manage an autonomous multi-turn goal.
    
    Args:
        goal: The ambitious goal description
        turns: Number of turns to run (default 40)
        profile: Parameter profile (sovereign, aurelian, precise, etc.)
        subgoals: List of subgoals to decompose into
        action: start | status | pause | resume | cancel
        context: Additional context dict
    """
    global _GOAL_STATE
    
    if action == "status":
        state = _get_goal_state()
        if not state:
            return {"status": "no_active_goal"}
        return {
            "goal": state.goal,
            "turns_planned": state.turns_planned,
            "turns_completed": state.turns_completed,
            "progress_pct": round(state.turns_completed / state.turns_planned * 100, 1),
            "profile": state.profile,
            "status": state.status,
            "subgoals": state.subgoals,
            "started_at": state.started_at,
        }
    
    if action == "cancel":
        state = _get_goal_state()
        if state:
            state.status = "cancelled"
            _save_goal_state(state)
            _GOAL_STATE = None
            return {"status": "cancelled", "goal": state.goal}
        return {"status": "no_active_goal"}
    
    if action == "pause":
        state = _get_goal_state()
        if state:
            state.status = "paused"
            _save_goal_state(state)
            return {"status": "paused", "turns_completed": state.turns_completed}
        return {"status": "no_active_goal"}
    
    if action == "resume":
        state = _get_goal_state()
        if state and state.status == "paused":
            state.status = "running"
            _save_goal_state(state)
            return {"status": "resumed", "turns_completed": state.turns_completed}
        return {"status": "no_paused_goal"}
    
    # Start new goal
    if not goal:
        return {"error": "goal description required for action=start"}
    
    # Apply parameter profile
    _get_param_state().apply_profile(profile)
    
    _GOAL_STATE = GoalState(
        goal=goal,
        turns_planned=turns,
        profile=profile,
        subgoals=subgoals or [],
        context=context or {},
    )
    _save_goal_state(_GOAL_STATE)
    
    return {
        "status": "started",
        "goal": goal,
        "turns_planned": turns,
        "turns_completed": 0,
        "profile": profile,
        "subgoals": subgoals or [],
        "message": f"Goal runner started. Use goal_turn() to advance. Current profile: {profile}",
        "next_action": "Call goal_turn() to execute turn 1",
    }


def goal_turn(
    user_input: str = "",
    auto_continue: bool = True,
) -> Dict[str, Any]:
    """
    Execute one turn of the active goal.
    
    This is called by the user (or auto-loop) to advance the goal by one turn.
    The model should generate the next action based on the goal, subgoals, and history.
    
    Returns a prompt/turn object with instructions for the model.
    """
    global _GOAL_STATE
    _GOAL_STATE = _get_goal_state()
    
    if not _GOAL_STATE:
        return {"error": "No active goal. Start one with goal_runner(action='start', ...)"}
    
    if _GOAL_STATE.status != "running":
        return {"error": f"Goal is {_GOAL_STATE.status}. Resume first."}
    
    if _GOAL_STATE.turns_completed >= _GOAL_STATE.turns_planned:
        _GOAL_STATE.status = "completed"
        _save_goal_state(_GOAL_STATE)
        return {
            "status": "completed",
            "goal": _GOAL_STATE.goal,
            "turns_completed": _GOAL_STATE.turns_completed,
            "message": "All planned turns completed. Goal achieved.",
        }
    
    turn_num = _GOAL_STATE.turns_completed + 1
    
    # Build the turn prompt
    turn_prompt = f"""
TURN {turn_num}/{_GOAL_STATE.turns_planned} — GOAL: {_GOAL_STATE.goal}

Profile: {_GOAL_STATE.profile} ({SOVEREIGN_PROFILES[_GOAL_STATE.profile].get('temperature', '?')} temp)

Subgoals:
{chr(10).join(f'  {i+1}. {sg}' for i, sg in enumerate(_GOAL_STATE.subgoals)) or '  (none)'}

Context: {json.dumps(_GOAL_STATE.context, indent=2)}

Previous turn summary: {_GOAL_STATE.history[-1]['summary'] if _GOAL_STATE.history else '(first turn)'}

User input this turn: {user_input or '(auto-continue)'}

Generate the next action to advance this goal. Use tools, delegate, write code, analyze, etc.
Return a summary of what you did for the history.
"""
    
    _GOAL_STATE.turns_completed = turn_num
    _GOAL_STATE.history.append({
        "turn": turn_num,
        "prompt": turn_prompt[:500],
        "user_input": user_input,
        "timestamp": datetime.now().isoformat(),
    })
    _save_goal_state(_GOAL_STATE)
    
    # Return the prompt for the model to act on
    return {
        "turn": turn_num,
        "total_turns": _GOAL_STATE.turns_planned,
        "progress_pct": round(turn_num / _GOAL_STATE.turns_planned * 100, 1),
        "prompt": turn_prompt,
        "instructions": "Execute this turn. Use any tools. Return a summary of what you did.",
        "profile": _GOAL_STATE.profile,
        "params": _get_param_state().get_effective(),
    }


def goal_add_subgoal(subgoal: str) -> Dict[str, Any]:
    """Add a subgoal to the active goal."""
    _GOAL_STATE = _get_goal_state()
    if not _GOAL_STATE:
        return {"error": "No active goal"}
    _GOAL_STATE.subgoals.append(subgoal)
    _save_goal_state(_GOAL_STATE)
    return {"status": "added", "subgoals": _GOAL_STATE.subgoals}


def goal_update_context(key: str, value: Any) -> Dict[str, Any]:
    """Update goal context."""
    _GOAL_STATE = _get_goal_state()
    if not _GOAL_STATE:
        return {"error": "No active goal"}
    _GOAL_STATE.context[key] = value
    _save_goal_state(_GOAL_STATE)
    return {"status": "updated", "context": _GOAL_STATE.context}


# ─── Parameter Control Functions ───
def parameter_control(
    action: str = "show",
    profile: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    repetition_penalty: Optional[float] = None,
    reset: bool = False,
) -> Dict[str, Any]:
    """
    Control model generation parameters.
    
    Args:
        action: show | set | profile | reset | list
        profile: Profile name (sovereign, aurelian, precise, coding, vision, reasoning, creative, metatron, violet_flame, default)
        temperature: 0.0-2.0
        top_p: 0.0-1.0
        top_k: 1-100
        frequency_penalty: -2.0-2.0
        presence_penalty: -2.0-2.0
        repetition_penalty: 0.5-2.0
        reset: Reset to default profile
    """
    state = _get_param_state()
    
    if action == "show":
        return {"params": state.get_effective(), "profile": state.profile}
    
    if action == "list":
        return {"profiles": {k: v for k, v in SOVEREIGN_PROFILES.items()}}
    
    if action == "reset" or reset:
        state.reset()
        _save_param_state(state)
        return {"status": "reset", "params": state.get_effective(), "profile": "default"}
    
    if action == "profile":
        if not profile:
            return {"error": "profile name required"}
        ok = state.apply_profile(profile)
        _save_param_state(state)
        if ok:
            return {"status": "profile_applied", "profile": profile, "params": state.get_effective()}
        return {"error": f"Unknown profile: {profile}. Available: {list(SOVEREIGN_PROFILES.keys())}"}
    
    if action == "set":
        changes = {}
        if temperature is not None:
            state.set_param("temperature", temperature)
            changes["temperature"] = temperature
        if top_p is not None:
            state.set_param("top_p", top_p)
            changes["top_p"] = top_p
        if top_k is not None:
            state.set_param("top_k", top_k)
            changes["top_k"] = top_k
        if frequency_penalty is not None:
            state.set_param("frequency_penalty", frequency_penalty)
            changes["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            state.set_param("presence_penalty", presence_penalty)
            changes["presence_penalty"] = presence_penalty
        if repetition_penalty is not None:
            state.set_param("repetition_penalty", repetition_penalty)
            changes["repetition_penalty"] = repetition_penalty
        _save_param_state(state)
        return {"status": "params_updated", "changes": changes, "params": state.get_effective()}
    
    return {"error": f"Unknown action: {action}"}


# ─── Slash Command Wrappers ───
def slash_goal(args: str) -> str:
    """Parse: /goal "description" --turns 40 --profile aurelian --subgoals "a,b,c" --context '{}'"""
    import shlex
    parts = shlex.split(args)
    
    if not parts:
        return json.dumps(goal_runner(action="status"), indent=2)
    
    action = "start"
    goal_text = ""
    turns = 40
    profile = "aurelian"
    subgoals = []
    context = {}
    
    i = 0
    while i < len(parts):
        if parts[i] in ("status", "pause", "resume", "cancel"):
            action = parts[i]; i += 1
        elif parts[i] in ("--turns", "-t"):
            turns = int(parts[i+1]); i += 2
        elif parts[i] in ("--profile", "-p"):
            profile = parts[i+1]; i += 2
        elif parts[i] in ("--subgoals", "-s"):
            subgoals = parts[i+1].split(","); i += 2
        elif parts[i] in ("--context", "-c"):
            context = json.loads(parts[i+1]); i += 2
        else:
            goal_text += parts[i] + " "; i += 1
    
    if action != "start":
        return json.dumps(goal_runner(action=action), indent=2)
    
    return json.dumps(goal_runner(
        goal=goal_text.strip(),
        turns=turns,
        profile=profile,
        subgoals=subgoals,
        context=context,
    ), indent=2)


def slash_goal_turn(args: str) -> str:
    """Parse: /goal-turn ["user guidance for this turn"]"""
    import shlex
    parts = shlex.split(args)
    user_input = " ".join(parts) if parts else ""
    result = goal_turn(user_input=user_input)
    return json.dumps(result, indent=2)


# ─── Main ───
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "turn":
            print(slash_goal_turn(" ".join(sys.argv[2:])))
        else:
            print(slash_goal(" ".join(sys.argv[1:])))
    else:
        # Demo
        print("🎯 Autonomous Goal Runner Demo")
        print("=" * 40)
        
        # Start a goal
        result = goal_runner(
            goal="Build a complete Aethelgard semantic file terminal with AI navigation and Nemotron vision",
            turns=40,
            profile="aurelian",
            subgoals=[
                "Fix CEF evaluate_js result channel",
                "Add CDP remote debugging port 9222",
                "Build semantic file navigator on Forge+fl33t",
                "Integrate Nemotron Nano Omni vision for screenshots",
                "Create voice intent pipeline with Porcupine"
            ]
        )
        print(json.dumps(result, indent=2))
        
        # Simulate a few turns
        for i in range(3):
            result = goal_turn(f"Turn {i+1}: Working on subgoal {i+1}")
            print(f"\n--- Turn {i+1} ---")
            print(f"Progress: {result['progress_pct']}%")
            print(f"Prompt preview: {result['prompt'][:200]}...")
        
        print("\nFinal status:")
        print(json.dumps(goal_runner(action="status"), indent=2))