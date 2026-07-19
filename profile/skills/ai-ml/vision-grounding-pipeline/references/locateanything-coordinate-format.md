# LocateAnything Coordinate Format Reference

## Raw Model Output
```
<ref>label</ref><box><x1><y1><x2><y2></box>
```

Where x1, y1, x2, y2 are integers in range [0, 1000] representing normalized coordinates.

## Coordinate System
- Origin (0,0) = top-left corner
- (1000, 1000) = bottom-right corner
- x increases left-to-right
- y increases top-to-bottom

## Conversion to Pixels
```python
def norm_to_pixels(box_norm, image_width, image_height):
    """Convert normalized [0-1000] box to pixel coordinates."""
    x1 = int(box_norm[0] / 1000 * image_width)
    y1 = int(box_norm[1] / 1000 * image_height)
    x2 = int(box_norm[2] / 1000 * image_width)
    y2 = int(box_norm[3] / 1000 * image_height)
    return [x1, y1, x2, y2]

def center_from_box(box_pixels):
    """Compute center point from pixel box."""
    cx = (box_pixels[0] + box_pixels[2]) // 2
    cy = (box_pixels[1] + box_pixels[3]) // 2
    return [cx, cy]
```

## Example
Input image: 800×600
Raw output: `<ref>button</ref><box><200><300><500><700></box>`

```python
box_norm = [200, 300, 500, 700]
box_px = norm_to_pixels(box_norm, 800, 600)
# box_px = [160, 180, 400, 420]
center = center_from_box(box_px)
# center = [280, 300]
```

## Parser Implementation
See `/home/craig/tools/locate_parser.py`:
- `parse_locate_response(response: str)` → extracts label, box_norm
- `normalize_to_pixels(box_norm, img_w, img_h)` → converts to pixels
- `draw_boxes(image_path, predictions, output_path)` → visual annotation

## Edge Cases
- Model may output `<box>None</box>` when no detection
- Box coordinates may be out of order (x2 < x1) — parser handles this
- Coordinates may exceed 1000 slightly (e.g., 1001) — clamp to 1000