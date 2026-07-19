---
name: creative-visual
description: "Visual creative tools — architecture diagrams, ASCII art/video, Excalidraw diagrams, p5.js sketches, HTML mockups"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, visual, diagrams, ascii, art, excalidraw, p5js, mockups, generative-art]
    related_skills: [creative-content, creative-media]
---

# Creative Visual Umbrella

Consolidated skill for all visual creative tools. Absorbs: architecture-diagram, ascii-art, ascii-video, excalidraw, p5js, sketch.

## Contents

1. [Architecture Diagrams (SVG/HTML)](#1-architecture-diagrams-svghtml)
2. [ASCII Art](#2-ascii-art)
3. [ASCII Video Production](#3-ascii-video-production)
4. [Excalidraw Diagrams](#4-excalidraw-diagrams)
5. [p5.js Sketches](#5-p5js-sketches)
6. [HTML Mockups (Sketch)](#6-html-mockups-sketch)

---

## 1. Architecture Diagrams (SVG/HTML)

Generate dark-themed, self-contained HTML files with inline SVG for architecture/infrastructure diagrams.

### Design System

- **Background**: Slate-950 (`#020617`) with 40px grid
- **Font**: JetBrains Mono (Google Fonts)
- **Sizes**: 12px names, 9px sublabels, 8px annotations

### Component Colors

| Component | Fill | Stroke |
|-----------|------|--------|
| Frontend | `rgba(8,51,68,0.4)` | `#22d3ee` (cyan) |
| Backend | `rgba(6,78,59,0.4)` | `#34d399` (emerald) |
| Database | `rgba(76,29,149,0.4)` | `#a78bfa` (violet) |
| AWS/Cloud | `rgba(120,53,15,0.3)` | `#fbbf24` (amber) |
| Security | `rgba(136,19,55,0.4)` | `#fb7185` (rose) |
| Message Bus | `rgba(251,146,60,0.3)` | `#fb923c` (orange) |
| External | `rgba(30,41,59,0.5)` | `#94a3b8` (slate) |

### Structure

Single self-contained `.html` file: Header → SVG diagram → Summary cards → Footer. No JS needed, no dependencies (except Google Fonts).

---

## 2. ASCII Art

Multiple tools for text-based art. All local or free APIs — no API keys required.

### Text Banners

**pyfiglet (local):**
```bash
python3 -m pyfiglet "YOUR TEXT" -f slant
python3 -m pyfiglet --list_fonts  # 571 fonts
```

**asciified API (remote, no install):**
```bash
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
```

### Cowsay

```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"
cowsay -l  # List 50+ characters
```

### Boxes (decorative borders)

```bash
echo "Hello World" | boxes -d stone
boxes -l  # List 70+ designs
```

### Image to ASCII

```bash
ascii-image-converter image.png -C
jp2a --width=80 --colors image.jpg
```

### Pre-Made ASCII Art

```bash
curl -s 'https://ascii.co.uk/art/cat' | python3 -c "import re,html,sys; [print(html.unescape(re.sub(r'<[^>]+>','',a)).strip()) for a in re.findall(r'<pre[^>]*>(.*?)</pre>',sys.stdin.read(),re.DOTALL) if len(a)>30]"
```

### Fun Utilities

- QR codes: `curl -s "qrenco.de/Hello+World"`
- Weather: `curl -s "wttr.in/London"`
- GitHub Octocat: `curl -s https://api.github.com/octocat`

---

## 3. ASCII Video Production

Convert video/audio to colored ASCII MP4/GIF. Full production pipeline with Python + ffmpeg.

### Pipeline: INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE

### Modes

- **Video-to-ASCII** — Recreates source footage with ASCII characters
- **Audio-reactive** — Generative visuals driven by audio features (FFT, bands, beats)
- **Generative** — Procedural ASCII animation from seed
- **Hybrid** — Video with audio-reactive overlays
- **Lyrics/text** — Timed text with visual effects

### Stack

Python 3, NumPy, SciPy, Pillow, ffmpeg. Single self-contained script per project.

### Brightness (Critical)

Use adaptive tonemap, never `canvas * N` multipliers:
```python
def tonemap(canvas, gamma=0.75):
    f = canvas.astype(np.float32)
    lo, hi = np.percentile(f[::4, ::4], [1, 99.5])
    f = np.clip((f - lo) / (hi - lo), 0, 1) ** gamma
    return (f * 255).astype(np.uint8)
```

---

## 4. Excalidraw Diagrams

Create hand-drawn style diagrams by writing Excalidraw JSON. Save as `.excalidraw` files — drag-drop onto excalidraw.com.

### Element Types

- `rectangle`, `ellipse`, `diamond`, `arrow`, `text`
- Container binding: shape has `boundElements`, text has `containerId`
- Arrow bindings: `startBinding` / `endBinding` with `elementId` + `fixedPoint`

### Color Palette

| Use | Fill |
|-----|------|
| Primary/Input | `#a5d8ff` (light blue) |
| Success/Output | `#b2f2bb` (light green) |
| Warning/External | `#ffd8a8` (light orange) |
| Processing | `#d0bfff` (light purple) |
| Error/Critical | `#ffc9c9` (light red) |
| Notes | `#fff3bf` (light yellow) |
| Storage | `#c3fae8` (light teal) |

### Sizing

- Minimum fontSize: 16 for body, 20 for titles
- Minimum shape size: 120x60 for labeled elements
- 20-30px minimum gaps between elements

---

## 5. p5.js Sketches

Interactive/generative visual art in the browser. Single self-contained HTML files with p5.js from CDN.

### Modes

Generative art, data viz, interactive experiences, animation, 3D (WebGL), image processing, audio-reactive.

### Structure

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.3/p5.min.js"></script>
<script>
const CONFIG = { seed: 42 };
const PALETTE = { bg: '#0a0a0f', primary: '#e8d5b7' };

function setup() { createCanvas(1920, 1080); randomSeed(CONFIG.seed); }
function draw() { /* render */ }
function keyPressed() {
  if (key === 's') saveCanvas('output', 'png');
  if (key === 'g') saveGif('output', 5);
}
</script>
```

### Key Practices

- `p5.disableFriendlyErrors = true` — before setup, removes 10x overhead
- `pixelDensity(1)` — prevent retina overdraw
- HSB color mode: `colorMode(HSB, 360, 100, 100, 100)`
- Use `createGraphics()` for layered composition
- Seeded randomness: always `randomSeed()` + `noiseSeed()`
- Export: PNG (`s`), GIF (`g`), frame sequence + ffmpeg for MP4

---

## 6. HTML Mockups (Sketch)

Quick throwaway HTML mockups: 2-3 design variants for comparison. Not production code — exploration only.

### Workflow

1. **Intake** — Feel, references, core action
2. **Variants** — 2-3 with different design stances (not different pixels)
3. **Build** — Self-contained HTML, realistic content, interactive elements
4. **Compare** — Head-to-head comparison table with opinionation
5. **Pick** — User selects winner or requests iteration

### Variant Axes

- Density: compact / airy / ultra-dense
- Emphasis: content-first / action-first / tool-first
- Aesthetic: editorial / utilitarian / playful
- Layout: single-column / sidebar / split-pane

### Variant Structure

```
sketches/001-calm-editorial/
├── index.html
└── README.md
```

Each README answers: design stance, key choices, trade-offs, best for.
