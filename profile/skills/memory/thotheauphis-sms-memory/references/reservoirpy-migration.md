# ReservoirPy v0.3 → v0.4+ Migration

## Breaking Changes
| v0.3 | v0.4+ | Reason |
|------|-------|--------|
| `from reservoirpy import ESN` | `from reservoirpy.nodes import Reservoir, Ridge` | `ESN` class removed |
| `ESN(input_dim=, reservoir_dim=, spectral_radius=)` | `Reservoir(units=, sr=)` + `Ridge()` | Decomposed into separate nodes |
| `model.fit(X, y)` | `states = reservoir.run(X); readout.fit(states, y)` | Two-step: reservoir then readout |
| `model.predict(X)` | `states = reservoir.run(X); readout.run(states)` | Same two-step |

## Readout Guard
Ridge readout must be fitted **before** first `run()`:
```python
if not hasattr(self.readout, 'Wout') or self.readout.Wout is None:
    return np.zeros((len(X), 1))  # not trained yet
states = self.reservoir.run(X)
return self.readout.run(states)
```

## Training
Minimum ~20 samples for a 32-unit reservoir. Fewer samples than reservoir units → singular covariance matrix in Ridge solve → `LinAlgError: A singular matrix detected`.
