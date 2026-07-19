# Grounding Object Class for Emerge Storage

```python
#!/usr/bin/env python3
"""
GroundingObject - Emerge-compatible class for storing vision grounding predictions.
Must be importable from emerge-node's Python environment.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class GroundingObject:
    """Grounding prediction as Emerge object."""
    
    # Required by emerge
    id: str
    path: str = "/groundings"
    name: str = "grounding"
    
    # Grounding data
    type: str = "grounding"
    label: str = ""
    box_norm: List[int] = field(default_factory=list)
    pixels: List[int] = field(default_factory=list)
    center: List[int] = field(default_factory=list)
    image_path: str = ""
    image_size: List[int] = field(default_factory=list)
    prompt: str = ""
    session_id: str = "default"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    vector_hash: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "source": "locateanything",
        "model": "locateanything-3b",
        "dimensions": 1024
    })
    
    def __post_init__(self):
        # Ensure required fields have defaults
        if not self.box_norm:
            self.box_norm = [0, 0, 0, 0]
        if not self.pixels:
            self.pixels = [0, 0, 0, 0]
        if not self.center:
            self.center = [0, 0]
        if not self.image_size:
            self.image_size = [800, 600]
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
```

## Installation for Emerge Node

```bash
# On the machine running emerge-node (or same user env):
pip install -e /home/craig/tools

# Or copy directly:
cp /home/craig/tools/grounding_object.py ~/.local/lib/python3.13/site-packages/

# Restart emerge-node
systemctl --user restart emerge-node
```