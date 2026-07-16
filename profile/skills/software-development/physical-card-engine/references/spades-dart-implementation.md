# Spades — Dart Implementation Reference

## Engine Layout

```
engine/
├── card.dart          — Suit, Rank, Card (+ JSON serialization)
├── deck.dart          — Deck.fresh(), Deck.fromBooks(), Deck.fromOrder()
├── book.dart          — Book, BookCollection, RakeStyle, ChunkArrangement
├── shuffle.dart       — StripShuffle, ShuffleSequence, applyShuffleSequence()
├── trick.dart         — Trick (+ winner resolution)
├── scoring.dart       — Bid, TeamRoundResult, TeamScore, bidsAreLegal()
├── game.dart          — GameState, gameReducer, DealSetup
├── ai.dart            — botBid(), botPlay()
└── test.dart          — 47 smoke tests
```

## Prison Spades Rules

- Ace high, no jokers
- Lead trump anytime (no need to break spades)
- 6-4 don't play, 5-5 don't play (sum ≠ 10, 13)
- Scoring: bid×10 if met, overtricks +1 each, bid 10 = 200
- No sandbags (overtricks are just points)
- Game ends at 350 points OR 2 ducks (sets)

## Key Bug Fixed: `clearTrick`/`currentTrick` Conflict

**Root cause:** In `GameState.copyWith()`:

```dart
currentTrick: clearTrick == true ? null : (currentTrick ?? this.currentTrick),
```

The `_play` function was passing both `currentTrick: Trick(winner)` AND `clearTrick: true`. The ternary evaluates `clearTrick == true` first, so the new `Trick(winner)` was silently discarded and replaced with `null`.

**Result:** Only the first trick ever completed. Every subsequent trick was immediately nullified. The game loop appeared to hang — `currentPlayer` was stuck at seat 0, `currentTrick` was always null, and `legalPlays` returned the full hand (no lead suit), so the bot kept leading its lowest card every iteration.

**Fix:** When creating a new trick after a completed one, pass ONLY `currentTrick: Trick(winner)` without `clearTrick`. Reserve `clearTrick: true` for the scoring phase (end of round).

```dart
// ✅ CORRECT — new trick, no clearTrick
return s.copyWith(
  currentPlayer: winner,
  currentTrick: Trick(winner),
);

// ✅ CORRECT — scoring, no new trick
return s.copyWith(
  phase: GamePhase.scoring,
  clearTrick: true,  // no more tricks
);
```

## Building Books from Completed Tricks

```dart
List<Book> _buildBooks(List<Trick> tricks, RakeStyle rakeStyle) {
  final books = List.generate(4, (_) => <Card>[]);
  for (final trick in tricks) {
    final winner = trick.winner();
    final raked = rakeTrick(trick.plays, trick.leader, winner, rakeStyle);
    books[winner].addAll(raked);
  }
  return [for (var i = 0; i < 4; i++) Book(i, books[i])];
}
```

The `rakeTrick()` function takes the 4 plays (in play order), the leader seat, the winner seat, and the rake style. Returns the 4 cards in the order they'd sit in the winner's book.

## First Deal vs Subsequent Deals

The `_deal` function checks `s.completedTricks.isEmpty && s.round == 1`:
- **First deal**: `Deck.fresh()` (standard ordered deck) + shuffle sequence
- **Subsequent deals**: Build books from `s.completedTricks`, assemble 3 chunks, apply shuffle sequence

### Thrown-In Detection

When a hand is thrown in (bids sum to 10 or 13), `completedTricks` is empty but `round > 1`. The detection condition:

```dart
if (s.completedTricks.isEmpty && s.round == 1) {
  // First deal — fresh deck
} else if (s.completedTricks.isEmpty && s.round > 1) {
  // Thrown-in redeal — books are sorted hands, not played-out tricks
  // Use BookCollection.fromSortedHands() + thrown-in shuffle sequence
} else {
  // Normal redeal — build books from completed tricks
}
```

The `nextRound()` action increments `round` and `dealer` but does NOT clear `completedTricks`. They're consumed by the next `_deal` call (which clears them in the new state via `completedTricks: []`).

## Testing Determinism

The engine is fully deterministic. Same inputs → same outputs every time. This is tested by:

```dart
// Same setup → same hands
var s1 = GameState(); s1 = gameReducer(s1, deal(setup: ...));
var s2 = GameState(); s2 = gameReducer(s2, deal(setup: ...));
// s1.hands == s2.hands — all 52 cards match

// Different chunk arrangement → different hands
var s1 = GameState(); s1 = gameReducer(s1, deal(setup: abc...));
var s2 = GameState(); s2 = gameReducer(s2, deal(setup: bac...));
// s1.hands != s2.hands — at most a few cards coincidentally match
```

## Code Style: 🏴 Territorial Landmarks

This user's explicit directive: **"very very very economically."** When a feature is discussed but not yet ready to implement:

- Do NOT build the feature body
- Plant a 🏴 landmark comment at the exact insertion point
- Include: why it matters (the physics/gameplay reason), the exact API shape needed, and a `TODO:`
- The landmark IS the deliverable

**Example from this session:**
```dart
  // 🏴 HANDEDNESS LANDMARK
  // First strip only: weak thumb bleeds extra cards when tension is
  // highest between the deck halves. Self-corrects immediately after.
  // Right-handed dealer's weak (left) thumb drops more from right pile.
  // Left-handed = reverse. Not a sustained bias — one-shot on strip 0.
  // TODO: add `int thumbDrop` — extra cards the weak hand bleeds on
  // the first strip of the first pass. 0 by default. Per-player.
```

Landmarks placed this session:
- `shuffle.dart` → HANDEDNESS (thumbDrop param), THROWN-IN (ShuffleSequence.thrownIn preset)
- `game.dart` → THROWN-IN DETECTION (else-if branch in _deal)
- `book.dart` → FROM SORTED HANDS (BookCollection.fromSortedHands() factory)

## Future Refinements (Captured from User)

These were discussed but not yet implemented. They belong in the engine's next iteration:

1. **Handedness bias**: One-shot on the **first strip only** where tension is highest. Weak hand drops MORE cards — right-handed dealer's weak left thumb bleeds extra from the right pile, then self-corrects. Left-handed reverses. Future `thumbDrop` int on `StripShuffle`, default 0, per-player metadata.

2. **Split range**: Real shuffle splits range 22/30 to 26/26. `_computeSplitPoint()` should model this as a distribution centered on 26 ±4 rather than a fixed value.

3. **Thumb drop**: The weak-hand thumb controls initial release. `thumbDrop` parameter controls how many extra cards the weak hand bleeds on the first strip of the first pass.

4. **Bottom stacking**: If the bottom ~7 cards of the pre-shuffle stack are spades, a 3-pass strip shuffle at 3-1-1-2 leaves them clustered in the last ~20 positions. The dealer can predict trump distribution.

5. **Thrown-in redeal sequence**: When a hand is thrown in (5-5/6-4), the 4 "books" are actually sorted hands (suits grouped). A `ShuffleSequence.thrownIn` preset tuned for suit-grouped input exploits this structure. The user can force a thrown-in to gain "absolute authority" over the deal.

6. **BookCollection.fromSortedHands()**: Factory for thrown-in redeals where no tricks were played — takes 4 sorted 13-card stacks directly.
