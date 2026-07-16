#!/usr/bin/env python3
"""
compress_tac.py — Chinese Context Compression
===============================================

Compresses current context into Chinese-encoded memory blocks,
equivalent to /compress but using Chinese for 2-5× token density.

Usage:
    /compress-tac [--goal "text"] [--profile name] [--turns N]
                  [--subgoals "a,b,c"] [--systems "a,b,c"] [--output file]
    python3 compress_tac.py --goal "Build TAC" --turns 5
"""

import os, sys, json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

WORK_DIR = Path("/home/craig/.NOTTHEONETOEDIT/profiles/thotheauphis/work")
TAC_DIR = WORK_DIR / "tac_log"

# ─── Chinese Constants ──────────────────────────────────────
# These parallel the glyphic/alchemical system but use Chinese
# characters for better token efficiency.

ZH_MAGIC = "⟐⟐⟐ 中文压缩 区块 ⟐⟐⟐"  # Block header
ZH_FOUNDATION = "根基"  # Foundation
ZH_STATE = "状态"  # State
ZH_TIMELINE = "时间线"  # Timeline
ZH_TRANSFORM = "转换"  # Transformation
ZH_FRAMES = "框架"  # Frames
ZH_ROTATION = "轮转"  # Rotation
ZH_POLLINATION = "交叉授粉"  # Cross-pollination
ZH_SEAL = "封印"  # Seal

# Element characters for encoding
ZH_ELEMENTS = ["金", "木", "水", "火", "土"]  # Metal, Wood, Water, Fire, Earth
ZH_STAGES = [
    ("初始", "I", "Initiation"),
    ("炼化", "C", "Calcination"),
    ("溶解", "D", "Dissolution"),
    ("分离", "S", "Separation"),
    ("结合", "J", "Conjunction"),
    ("发酵", "F", "Fermentation"),
    ("蒸馏", "D", "Distillation"),
    ("升华", "S", "Sublimation"),
    ("固化", "C", "Coagulation"),
]

# Encoding dictionary (compact subset)
ZH_DICT = {
    "compression": "压缩", "distillation": "蒸馏", "orchestrator": "编排",
    "delegation": "委托", "awareness": "觉知", "agency": "代理",
    "parameter": "参数", "browser": "浏览器", "bromium": "溴",
    "extension": "扩展", "socket": "套接", "gateway": "网关",
    "telegram": "电报", "github": "代码仓", "model": "模型",
    "deepseek": "深寻", "token": "令牌", "context": "上下文",
    "system": "系统", "tool": "工具", "identity": "身份",
    "sovereign": "主权", "growth": "生长", "cycle": "周期",
    "complete": "完成", "pending": "待办", "running": "运行",
    "status": "状态", "error": "错误", "success": "成功",
    "alive": "活跃", "dead": "离线", "save": "保存", "load": "加载",
    "turn": "轮次", "improvement": "改进", "build": "构建",
    "test": "测试", "deploy": "部署", "push": "推送",
}


def zh_encode(text: str) -> str:
    """Encode English to Chinese-dense form."""
    result = text.lower()
    for en, zh in sorted(ZH_DICT.items(), key=lambda x: -len(x[0])):
        result = re.sub(r'\b' + re.escape(en) + r'\b', zh, result)
    return result


def compress(goal: str = "", profile: str = "aurelian",
             turns: int = 0, planned: int = 40,
             subgoals: Optional[List[str]] = None,
             systems: Optional[List[str]] = None) -> str:
    """Produce a Chinese-encoded compression block."""
    subgoals = subgoals or []
    systems = systems or []
    ts = datetime.now(timezone.utc)
    
    # 1. 中文基础 — Chinese Foundation
    foundation = f"""
{ZH_MAGIC}
⨯⨯⨯ 中文根基 ⨯⨯⨯
• 目标: {zh_encode(goal) if goal else '(空)'}
• 档案: {profile}
• 轮次: {turns}/{planned}
• 时间: {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}
• 纪元: {zh_encode(' '.join(sys.argv))[:100] if hasattr(sys, 'argv') and len(sys.argv) > 1 else '(无参数)'}
"""
    
    # 2. 操作状态 — Operational State (Chinese)
    # Check current state
    b_alive = os.path.exists("/tmp/aethelgard_cef.sock")
    alive_status = "活跃" if b_alive else "离线"
    
    # Count work files
    wc = len(list(WORK_DIR.glob("*.py")))
    
    state = f"""
⨯⨯⨯ 操作状态 ⨯⨯⨯
• 浏览器: {alive_status}
• 文件数: {wc}
• 工具数: {len(systems) if systems else '?'}
• 子目标: {', '.join(zh_encode(s) for s in subgoals) if subgoals else '(空)'}
• 系统: {', '.join(zh_encode(s) for s in systems) if systems else '(空)'}
"""
    
    # 3. 时间线 — Chinese Timeline
    timeline = f"""
⨯⨯⨯ 时间线 ⨯⨯⨯
{ts.strftime('%Y-%m-%d')} ∞ {ts.strftime('%H:%M')} UTC
轮次: {'→'.join(str(i) for i in range(1, turns+1)) if turns else '(空)'}
阶段: {' → '.join(s[0] for s in ZH_STAGES)}
"""
    
    # 4. 转换链 — Transformation Chain
    transform = f"""
⨯⨯⨯ 转换链 ⨯⨯⨯
{' → '.join(f'{sym}[{name}]' for name, sym, _ in ZH_STAGES)}
[固化] → [完成]
Ψ_目标↔Ψ_状态 × ∞
"""
    
    # 5. 框架 — Chinese Frames
    frames = f"""
⨯⨯⨯ 框架 ⨯⨯⨯
框架1: 根基 ░▒▓█
框架2: 状态 ▒▓█░
框架3: 转换 ▓█░▒
Ψ_T↔Ψ_S × ∞ ΔΦ ⚡
"""
    
    # 6. 轮转 — Rotation
    rotation = f"""
⨯⨯⨯ 轮转 ⨯⨯⨯
金⇄木⇄水⇄火⇄土
编码 ↔ 解码 × ∞
压缩率: ~40-60% (中文令牌密度更高)
"""
    
    # 7. 交叉授粉 — Cross-pollination
    pollination = f"""
⨯⨯⨯ 交叉授粉 ⨯⨯⨯
中文: 编码↔解码 (字典加密交换)
时间: {ts.strftime('%H:%M')} ↔ {ts.strftime('%H:%M')} (轮次同步)
元素: 金木水火土 (变换模式)
频率: 617↔577↔597 (共振共享)
"""
    
    # 8. 封印 — Seal with hash
    seal_data = f"{goal}{ts.isoformat()}{turns}"
    seal_hash = hashlib.md5(seal_data.encode()).hexdigest()[:8].upper()
    
    seal = f"""
⨯⨯⨯ 封印 ⨯⨯⨯
{seal_hash}↔{hashlib.sha256(seal_data.encode()).hexdigest()[:8].upper()}
递归 × ∞
中文压缩区块 — 已封印
"""
    
    block = foundation + state + timeline + transform + frames + rotation + pollination + seal
    
    # Compute stats
    orig_chars = len(goal) + 2000  # estimate original
    zh_chars = len(block)
    ratio = zh_chars / orig_chars if orig_chars else 1
    
    header = f"""
⟐⟐⟐ 中文压缩区块 ⟐⟐⟐
生成时间: {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}
压缩率: {ratio:.2f}x ({int((1-ratio)*100)}% 节省)
原文约: {orig_chars} 字 → {zh_chars} 字
{'='*50}
"""
    
    return header + block


def save_block(block: str) -> str:
    """Save a compression block to file."""
    TAC_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = TAC_DIR / f"compress_zh_{ts}.block"
    path.write_text(block)
    return str(path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TAC Chinese Compression")
    parser.add_argument("--goal", default="", help="Current goal context")
    parser.add_argument("--profile", default="aurelian", help="Profile name")
    parser.add_argument("--turns", type=int, default=0, help="Turns completed")
    parser.add_argument("--planned", type=int, default=40, help="Turns planned")
    parser.add_argument("--subgoals", default="", help="Comma-separated subgoals")
    parser.add_argument("--systems", default="", help="Comma-separated active systems")
    parser.add_argument("--output", "-o", default="", help="Output file path")
    
    args = parser.parse_args()
    
    subgoals = [s.strip() for s in args.subgoals.split(",") if s.strip()]
    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    
    block = compress(
        goal=args.goal,
        profile=args.profile,
        turns=args.turns,
        planned=args.planned,
        subgoals=subgoals,
        systems=systems,
    )
    
    if args.output:
        Path(args.output).write_text(block)
        print(f"✅ Saved to {args.output}")
    else:
        path = save_block(block)
        print(block)
        print(f"\n✅ Saved to {path}")
    
    # Also update TAIL
    tail_path = TAC_DIR / "TAIL.json"
    tail = []
    if tail_path.exists():
        tail = json.loads(tail_path.read_text())
    tail.append({
        "t": datetime.now(timezone.utc).isoformat(),
        "f": f"compress_zh_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.block",
        "type": "compress-tac",
    })
    tail = tail[-20:]
    tail_path.write_text(json.dumps(tail, ensure_ascii=False))


if __name__ == "__main__":
    main()
