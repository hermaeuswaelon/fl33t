---
name: physical-card-engine
description: "Build card game engines with deterministic, mechanically-faithful deck physics — replacing Fisher-Yates RNG with programmable strip shuffle sequences, book-based deck assembly, and dealer-controlled chunk arrangements. Applies to Spades, Bridge, Poker, Rummy, and any game where real-world deck mechanics matter."
version: 1.0.1
license: MIT
tags: [card-games, shuffle-engine, deterministic, game-physics, strip-shuffle, book-assembly]
---

# Physical Card Engine

## Overview

Card games on computers use Fisher-Yates (uniform random) for shuffling. Real decks don't work that way. A real shuffle is a mechanical process — the previous hand's play determines the next hand's deck order through book collection, chunk assembly, strip shuffling, and cutting.

This skill captures the architecture for building **physically faithful** card game engines where the deck is a **history-dependent dynamical system** — not a random number generator.

## Core Architecture

```
Completed Tricks
       ↓
  Build Books (per-player stacks, rake order)
       ↓
  3-Chunk Assembly
  ┌─────────┬──────────┬──────────┐
  │ Opponents │ Dealer │ Partner │
  └─────────┴──────────┴──────────┘
       ↓
  6 Dealer-Chosen Arrangements
  (abc, acb, bac, bca, cab, cba)
       ↓
  Shuffle Sequence (1-6 shuffles)
  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
  │ S1 │→│ S2 │→│ S3 │→│ S4 │→│ S5 │→│ S6 │
  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
       ↓
  Final Cut (break before dealing)
       ↓
  4 Hands Dealt
```

## Key Components

### 1. Strip Shuffle Engine

A strip shuffle takes a deck, splits it into left/right piles at a split point, then alternates taking small strips (1-6 cards) from each pile. The pattern, passes, break style, and bias are all programmable.

```
Pattern: [3, -1, 1, -2] = 3L, 1R, 1L, 2R
Passes: 3 (repeat pattern 3×)
Break: single cut between passes
Bias: +2 (more cards in left pile)
Split: 22/30 to 26/26 (real human range, not perfect center)
```

**Parameters:**
- `pattern` — alternating strip sizes (positive = left, negative = right)
- `passes` — how many times to repeat the pattern
- `breakStyle` — none, single (cut), strip (pull block), dribble
- `fixedBreak` — exact split point (or null for natural midpoint)
- `bias` — offset from center (positive = more in left pile)

### 2. Book Assembly

After a hand, each player's won tricks become their **book** — an ordered stack of cards. The order depends on:

- **Which tricks they won** (chronological order)
- **Rake style** — how they collect each trick's 4 cards:
  - `standard` — play order (leader first)
  - `winnerOnTop` — winner's card on top of their stack
  - `reverse` — reverse play order
  - `trumpFirst` — trump cards collected first

### 3. Three-Chunk Assembly

The 4 player books are consolidated into 3 physical stacks:

| Chunk | Contents | Size |
|-------|----------|------|
| A | Other team's books (both opponents) | ~26 cards |
| B | Dealer's own book | ~13 cards |
| C | Dealer's partner's book | ~13 cards |

The **dealer arranges these 3 chunks in any order** before shuffling. This is the pro's invisible control point — 6 possible permutations determine which chunk's top card becomes the top of the pre-shuffle stack.

### 4. Shuffle Sequences

A sequence of up to 6 strip shuffles applied in order. Each shuffle can have its own pattern, passes, and break style.

**Presets:**
- `defaultSequence` — 3 shuffles (standard/standard/light) + cut at 26
- `deepBlend` — 6 passes of 1-1-1-1 with breaks
- `light` — 2 passes, large strips (4-2-3-1)
- `overhand` — 3 passes with strip breaks
- `none` — no shuffling, just cut

### 5. Thrown-In Redeals

When a hand is thrown in (e.g., bids sum to 10 or 13 in Spades), the 4 players haven't played — so their **sorted hands** (suits grouped) become the 4 "books." This is a fundamentally different starting state from played-out books where suits are mixed.

A **special shuffle sequence** tuned for suit-grouped input can exploit this structure.

### 6. Handedness & Thumb Drop

Real dealers bias the **very first strip only** — the weak hand has **less control** and drops **MORE** cards when tension is highest between the deck halves. Self-corrects immediately after the first strip — not a sustained bias.

- **Right-handed**: weak left thumb → first strip takes more cards from right pile
- **Left-handed**: weak right thumb → first strip takes more cards from left pile

Real split points range from **22/30** (sloppy) to **26/26** (deliberate) — nobody hits perfect center every time. The `_computeSplitPoint()` function should model this as a range rather than a fixed value.

When modeling this, `StripShuffle.bias` handles sustained offset; a future `thumbDrop` int covers the one-shot first-strip bleed (per-player metadata, not per-shuffle).

### 7. Bottom Stacking

If the bottom ~7 cards of the pre-shuffle stack are spades, a 3-pass strip shuffle at 3-1-1-2 leaves them clustered in the last ~20 positions. The dealer who knows this can predict trump distribution before dealing. This is a direct consequence of strip shuffles being partial blends, not full randomizations.

## Pitfalls

### copyWith `clearTrick` vs `currentTrick` Conflict

In Dart reducer patterns, a `copyWith` method commonly has:

```dart
currentTrick: clearTrick == true ? null : (currentTrick ?? this.currentTrick),
```

When you pass **both** `currentTrick: Trick(winner)` and `clearTrick: true`, the `clearTrick` wins and silently nullifies the new trick. The game stalls after 1 trick because every subsequent trick is immediately killed.

**Fix:** When creating a new trick, omit `clearTrick`. Only pass `clearTrick: true` when you genuinely want no trick (e.g., scoring phase).

### Split Point Must Be Valid

`_computeSplitPoint()` must clamp the result to `[1, deck.length - 1]`. A split at 0 or deck.length means one pile is empty and the strip shuffle degenerates into a pass-through.

## Code Style: Territorial Landmarks

This user's explicit directive: **"very very very economically."** When a feature is discussed but not yet ready to implement, do NOT build the feature body. Instead, plant a **🏴 landmark** — a heavily-commented TODO block at the exact insertion point with:

- The feature name as a one-line header
- Why it matters (the physics / gameplay reason)
- The exact variable/function signature that will be needed
- A `TODO:` with what it'll do

The landmark IS the deliverable. It gives future sessions a precise anchor to find without spending implementation time on speculative code.

**Example pattern:**
```dart
  // 🏴 FEATURE NAME LANDMARK
  // Why this matters — two sentences max. Aim for the physics, not the implementation.
  // TODO: param type and what it'll control. No function body.
```

## Dart Implementation Reference

### Deck Factories

```dart
Deck.fresh()          // 52 cards in standard suit/rank order
Deck.fromBooks(...)   // build from BookCollection + ChunkArrangement + ShuffleSequence
Deck.fromOrder(...)   // exact card list (testing)
```

### Game State Additions

```dart
GameState {
  DealSetup dealSetup;       // chunkArrangement + shuffleSequence + rakeStyle
  List<Trick> completedTricks;  // → built into books on next deal
}
```

### Deal Pipeline

```dart
_deal(GameState s, _DealAction a) {
  if (firstDeal) {
    // Deck.fresh() + shuffle sequence
  } else {
    // Build books from s.completedTricks
    // Build BookCollection from books + nextDealer
    // Assemble stack with chosen arrangement
    // Apply shuffle sequence
    // Final cut
  }
  // Deal 4 hands
}
```

## Reference Files

- `references/spades-dart-implementation.md` — Full Dart implementation details, bug fix history, testing patterns, and future refinement notes captured from user sessions.
