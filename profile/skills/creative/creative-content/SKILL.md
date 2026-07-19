---
name: creative-content
description: "Content-focused creative tools — HTML artifacts, design tokens, pretext demos, design system clones, text humanization"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [creative, content, design, html, pretext, typography, web-design, humanizer]
    related_skills: [creative-visual, creative-media]
---

# Creative Content Umbrella

Consolidated skill for content-focused creative tools. Absorbs: claude-design, design-md, pretext, popular-web-designs, humanizer.

## Contents

1. [HTML Artifacts (Claude Design)](#1-html-artifacts-claude-design)
2. [DESIGN.md Token Specs](#2-designmd-token-specs)
3. [Pretext Browser Demos](#3-pretext-browser-demos)
4. [Popular Web Design Systems](#4-popular-web-design-systems)
5. [Text Humanization](#5-text-humanization)

---

## 1. HTML Artifacts (Claude Design)

Create polished, single-file HTML artifacts for landing pages, decks, prototypes, and interactive presentations. One file, all inline — no build step.

### Guidelines

- Single self-contained HTML file (CSS + JS inline)
- System fonts or one Google Font via `<link>`
- Optional: Tailwind via CDN for utility-first styling
- Realistic content (not lorem ipsum)
- Responsive design included

### Typical Use Cases

- Landing pages, product demos, pitch decks
- Interactive prototypes, status dashboards
- Portfolio pieces, microsites, documentation pages

---

## 2. DESIGN.md Token Specs

Author, validate, and export Google-style DESIGN.md token specification files. These define design tokens (colors, typography, spacing, components) in a standardized format for AI agents and design systems.

### Token Categories

- **Color** — Primary, secondary, accent, neutral, semantic (success, warning, error)
- **Typography** — Font families, sizes, weights, line heights
- **Spacing** — Scale (4px/8px base), padding, margin, gap
- **Border** — Radius, width, style
- **Shadow** — Elevation levels
- **Animation** — Duration, easing, delay
- **Layout** — Breakpoints, container widths, grid columns

### Format

YAML frontmatter + markdown body. Each token has: name, value, description, and optional alias/reference.

---

## 3. Pretext Browser Demos

Build creative browser demos using [@chenglou/pretext](https://github.com/chenglou/pretext) — DOM-free text layout for ASCII art, typographic flow around obstacles, text-as-geometry games, kinetic typography, and text-powered generative art.

### Features

- DOM-free: renders directly to canvas or terminal
- Text layout with arbitrary obstacles and paths
- ASCII art generation with precise character placement
- Kinetic typography with animation support
- Single-file HTML output by default

---

## 4. Popular Web Design Systems

Access 54 real design system references from companies like Stripe, Linear, Vercel, and more. Use these as inspiration and reference for UI/UX design.

### Design Systems Included

- **Stripe** — Payment UI, clean data tables, gradient accents
- **Linear** — Issue tracking, board views, dark theme
- **Vercel** — Geist font, geometry grid, minimal navigation
- **Radix UI** — Accessible primitives, unstyled components
- **shadcn/ui** — Copy-paste components, Tailwind-based

### How to Use

Search for specific patterns (nav, cards, forms, tables) and adapt to your project. These are reference implementations in HTML/CSS, not frameworks.

---

## 5. Text Humanization

Strip AI-isms from generated text and add authentic human voice. Removes clichés, hedging language, over-formality, and robotic phrasing.

### What It Removes

- "In today's digital landscape", "let's dive in", "it's worth noting"
- Overuse of "delve", "navigate", "leverage", "robust"
- Unnecessary hedging: "I think", "perhaps", "arguably"
- Formulaic structures: "not only... but also", "as we've seen"
- Over-polite closings, admission of AI-ness ("as an AI")

### What It Adds

- Natural sentence fragments, contractions
- Varied sentence length and structure
- Domain-appropriate vocabulary
- Personal anecdotes or perspective (when appropriate)
- Confidence without arrogance

### Usage

Feed text through the humanizer when the user wants "make this sound less AI-generated" or "give this more personality."
