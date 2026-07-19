---
name: creative-media
description: "Media-focused creative tools — ComfyUI, Manim animations, music/songwriting, infographics, TouchDesigner"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, media, comfyui, manim, animation, music, songwriting, infographic, touchdesigner]
    related_skills: [creative-visual, creative-content]
---

# Creative Media Umbrella

Consolidated skill for media-focused creative tools. Absorbs: comfyui, manim-video, songwriting-and-ai-music, baoyu-infographic, touchdesigner-mcp.

## Contents

1. [ComfyUI (Image/Video/Audio Generation)](#1-comfyui-imagevideoaudio-generation)
2. [Manim CE Animations](#2-manim-ce-animations)
3. [Songwriting & AI Music](#3-songwriting--ai-music)
4. [Infographics (Baoyu)](#4-infographics-baoyu)
5. [TouchDesigner MCP](#5-touchdesigner-mcp)

---

## 1. ComfyUI (Image/Video/Audio Generation)

Generate images, video, and audio with ComfyUI. Uses official `comfy-cli` for lifecycle management and REST/WebSocket API for execution.

### Setup

```bash
comfy-cli install
comfy-cli launch --background
```

### Capabilities

- Image generation (Stable Diffusion, Flux, etc.)
- Video generation with frame interpolation
- Audio/sound generation
- Workflow management with parameter injection
- Node/model management via comfy-cli

### Usage

- Launch ComfyUI, define workflows via the node editor or load existing ones
- Inject parameters programmatically via API
- Manage models and nodes with comfy-cli

---

## 2. Manim CE Animations

Create mathematical/animation videos using Manim Community Edition (the 3Blue1Brown animation engine).

### Setup

```bash
pip install manim
```

### Usage

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        self.play(Create(circle))
        self.play(Transform(circle, square))
```

### Render

```bash
manim -pql scene.py MyScene  # Low quality preview
manim -pqh scene.py MyScene  # High quality export
```

### Key Classes

- Shapes: `Circle`, `Square`, `Triangle`, `Polygon`, `Line`, `Arrow`
- Text: `Text`, `Tex` (LaTeX), `MathTex`
- Animations: `Create`, `Transform`, `FadeIn`, `FadeOut`, `MoveAlongPath`
- Layout: `VGroup`, `HGroup`, `Grid`
- Customization: `color`, `stroke_width`, `fill_opacity`, `scale`

---

## 3. Songwriting & AI Music

Craft song lyrics and generate music with Suno AI and similar platforms.

### Songwriting Craft

- Structure: verse, chorus, bridge, outro
- Rhyme schemes: AABB, ABAB, free verse
- Meter and rhythm patterns
- Lyric writing techniques: imagery, metaphor, alliteration
- Genre-specific conventions

### Suno AI Music Prompts

- Style prompts: genre, BPM, instruments, mood
- Lyric structure: sections, repeats, ad-libs
- Vocal style: harmony, backing vocals, spoken word
- Production: reverb, compression, stereo width

### Workflow

1. Define song structure and theme
2. Write lyrics with rhythmic scansion
3. Compose style prompt for Suno
4. Generate and iterate on outputs

---

## 4. Infographics (Baoyu)

Create rich infographics using 21 layouts × 21 styles. Supports Chinese (信息图, 可视化) and English content.

### Layout Types

- Timeline, comparison, flowchart, hierarchy
- Data dashboard, stats grid, step-by-step guide
- Process diagram, org chart, roadmap
- Checklist, card grid, feature comparison

### Styles

- Modern, minimalist, editorial, corporate
- Playful, hand-drawn, tech, dark mode
- Retro, gradient, glassmorphism, neumorphism

### Output

Self-contained HTML or image file. Data-driven with customizable colors and fonts.

---

## 5. TouchDesigner MCP

Control a running TouchDesigner instance via the twozero MCP protocol. 36 native tools for operator manipulation.

### Capabilities

- Create, delete, and modify operators (OPs)
- Set parameters (values, expressions, DAT/CHOP references)
- Wire connections between operators
- Execute Python scripts in TouchDesigner
- Build real-time visual compositions
- Manage timelines, renders, and outputs

### Connection

TouchDesigner must be running with the MCP server enabled. Interact via:
- Create operators by type (TOP, CHOP, SOP, DAT, MAT)
- Set parameter values
- Navigate and edit node networks
- Execute TD Python scripts

### Use Cases

- Automated visual generation pipelines
- Real-time VJ content creation
- Generative art installations
- Audio-reactive visualization systems
