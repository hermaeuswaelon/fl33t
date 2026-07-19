# Parallel Batch Grounding Pattern

## Overview
The `ParallelExecutorNode` pattern (from `state_machine.py`) enables zero-LLM-overhead batch processing of multiple screenshots against multiple prompts. This is the primary scaling mechanism for processing 10+ screenshots.

## Architecture

```
Workflow State
      │
      ▼
┌─────────────────────────────────────┐
│  BatchGroundingNode (ParallelExecutor) │
│  max_workers=4                       │
│                                      │
│  Tasks: [{task_id, image, prompt}, ...]│
└──────────────────┬────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    Worker 1            Worker N
    (thread)            (thread)
         │                   │
         ▼                   ▼
   vision_router.py   vision_router.py
   (subprocess)       (subprocess)
         │                   │
         └─────────┬─────────┘
                   ▼
        Aggregated Results
                   │
                   ▼
        UIMapAggregatorNode
        (deduplication)
```

## Implementation

### BatchGroundingNode (extends ParallelExecutorNode)
```python
class BatchGroundingNode(ParallelExecutorNode):
    def __init__(self, name: str = "batch_grounding", max_workers: int = 4):
        super().__init__(name, {})
        self.max_workers = max_workers
    
    def execute(self, state: Dict) -> Dict:
        tasks = state.get("batch_tasks", [])  # list of {task_id, image_path, prompt}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(run_single_grounding, task): task for task in tasks}
            
            results = []
            for future in as_completed(futures):
                task = futures[future]
                result = future.result()
                results.append(asdict(result))
        
        return {**state, "batch_results": results}
```

### run_single_grounding (subprocess call)
```python
def run_single_grounding(task: BatchTask) -> BatchResult:
    cmd = [
        sys.executable, "/home/craig/tools/vision_router.py",
        "--image", task.image_path,
        "--prompt", task.prompt,
        "--resize", str(task.resize[0]), str(task.resize[1])
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    # Parse JSON output, return BatchResult
```

## Performance Characteristics

| Workers | 10 images × 5 prompts | Speedup |
|---------|----------------------|---------|
| 1       | ~120s                | 1x      |
| 2       | ~65s                 | 1.8x    |
| 4       | ~35s                 | 3.4x    |
| 8       | ~25s                 | 4.8x    |

Bottleneck: GPU memory (all workers share same 3 model servers)

## Usage

### CLI
```bash
python3 batch_grounding.py \
  --images screen1.png screen2.png screen3.png \
  --prompts "button" "icon" "text field" "menu" \
  --workers 4 \
  --output ui_map.json
```

### Workflow Integration
```python
from state_machine import Workflow
from batch_grounding import BatchGroundingNode, UIMapAggregatorNode

wf = Workflow("batch_grounding")
wf.add_node(BatchGroundingNode("batch", max_workers=4))
wf.add_node(UIMapAggregatorNode("aggregate"))
wf.set_entry("batch")
wf.add_edge("batch", "aggregate")
wf.set_exit("aggregate")

initial_state = {
    "session_id": "batch_001",
    "batch_tasks": [
        {"task_id": "t1", "image_path": "a.png", "prompt": "button", "resize": [800, 600]},
        # ...
    ]
}

result = wf.compile().run(initial_state)
ui_map = result["ui_map"]
```

## UI Map Aggregation

The `UIMapAggregatorNode` deduplicates detections across prompts/images:

```python
def _deduplicate(self, elements: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    """Remove duplicate detections by IOU + label match."""
    kept = []
    for elem in elements:
        box = elem.get("box_norm", [0,0,0,0])
        is_dup = False
        for kept_elem in kept:
            kept_box = kept_elem.get("box_norm", [0,0,0,0])
            if iou(box, kept_box) > iou_threshold and elem["label"] == kept_elem["label"]:
                is_dup = True
                break
        if not is_dup:
            kept.append(elem)
    return kept
```

## Output Format (ui_map.json)
```json
{
  "session_id": "batch_001",
  "timestamp": "2026-07-18T23:00:00.000000",
  "images": [
    {
      "image_path": "screen1.png",
      "image_size": [800, 600],
      "elements": [
        {"label": "button", "box_norm": [100,200,300,400], "pixels": [...], "center": [...], "source_prompt": "button", "model": "locateanything-3b"},
        {"label": "icon", "box_norm": [50,50,150,150], "pixels": [...], "center": [...], "source_prompt": "icon", "model": "locateanything-3b"}
      ],
      "prompts_used": ["button", "icon"]
    }
  ],
  "total_elements": 42,
  "unique_labels": ["button", "icon", "text field", "menu"],
  "batch_stats": {"total": 50, "succeeded": 48, "failed": 2, "total_ms": 35000}
}
```

## Checkpointing
Every node execution creates a checkpoint:
```
~/.hermes/work/checkpoints/batch_grounding/
├── step_001_batch_grounding.json
├── step_002_aggregate.json
└── step_003_final.json
```

Resume with:
```python
wf = Workflow("batch_grounding")
# ... add nodes ...
wf.set_checkpoint_manager(CheckpointManager("~/.hermes/work/checkpoints/batch_grounding"))
wf.enable_auto_checkpoint(["batch", "aggregate"])
result = wf.compile().run(initial_state, resume_from="step_002_aggregate")
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Workers hang | GPU OOM | Reduce `max_workers` or model context |
| Timeout | Large images | Resize to 800×600 before routing |
| Duplicate detections | Multiple prompts hit same element | Aggregator IOU dedup handles this |
| Partial results | One worker crashes | Checkpoint recovers completed work |