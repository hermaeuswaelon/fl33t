# State Machine Workflow Patterns Reference

Documents the LangGraph-style state machine patterns used for autonomous workflows.

## Core Components (state_machine.py)

### Workflow
- `Workflow(name)` - Creates a new workflow
- `add_node(node)` - Adds a node (ExecutorNode, ParallelExecutorNode, etc.)
- `set_entry(node_name)` - Sets entry point
- `set_exit(node_name)` - Sets exit point
- `compile()` - Compiles to executable graph
- `run(initial_state)` - Executes workflow

### Node Types
- `ExecutorNode(name, tool_calls)` - Single-threaded tool batch execution
- `ParallelExecutorNode(name, branch_tools)` - Parallel branch execution
- `ConditionalNode(name, condition_fn, true_node, false_node)` - Branching
- `CheckpointNode(name, manager)` - State persistence

### CheckpointManager
- `CheckpointManager(dir)` - Manages step checkpoints
- `save(name, state)` - Manual checkpoint
- `load(name)` - Restore state
- `auto_checkpoint(nodes)` - Enable auto-save at node boundaries

## Vision Grounding 3-Tier Pattern

```python
# Architect → Foreman → Doer → Aggregator
wf = Workflow("vision_grounding")
wf.add_node(ArchitectNode())      # Decompose goal → prompts
wf.add_node(ForemanNode())        # Structure, validate, prioritize
wf.add_node(DoerNode())           # ParallelExecutorNode for batch grounding
wf.add_node(AggregatorNode())     # Synthesize UI map

wf.set_entry("architect")
wf.add_edge("architect", "foreman")
wf.add_edge("foreman", "doer")
wf.add_edge("doer", "aggregator")
wf.set_exit("aggregator")

wf.enable_auto_checkpoint(["architect", "foreman", "doer", "aggregator"])
```

## Key Patterns

### Parallel Batch Execution
```python
class DoerNode(ParallelExecutorNode):
    def execute(self, state):
        tasks = [GroundingTask(**t) for t in state["grounding_tasks"]]
        # Batch size 4 for parallel grounding
        results = run_batch_grounding(tasks, batch_size=4)
        return {**state, "results": results}
```

### Checkpoint Resume
```python
wf.run(initial_state, resume_from="foreman")  # Resume from foreman checkpoint
```

### State Schema
```python
{
    "goal": str,
    "image_path": str,
    "session_id": str,
    "grounding_tasks": List[dict],
    "grounding_results": List[dict],
    "sva_vector_ids": List[str],
    "ui_map": dict,
    "tier": str,  # architect_done, foreman_done, doer_done, aggregator_done
    "checkpoint": str
}
```