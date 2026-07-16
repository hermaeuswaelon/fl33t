# ZODB Persistence Bridge

## Architecture
- **Primary**: ZODB FileStorage (`vsa_vectors.fs`) — transactional, crash-safe
- **Fallback**: Pickle cache (`<db_path>.pkl`) — used when ZODB not importable
- **Cache isolation**: Each `db_path` gets its own `.pkl` file to prevent cross-contamination

## Key Rules
1. Vector metadata stored as `{"data": item}` dict; item may be numpy array — use `is not None`, never `if item`.
2. After storing vectors, call `transaction.commit()` (ZODB mode) or `_save_fallback()` (pickle mode).
3. On `close()`, flush and release file locks.

## API
```python
store = PersistentVSAStore(db_path=Path("/path/to/v.fs"))
store.store_vector(key, vector_ndarray, metadata_dict)
vec = store.load_vector(key)
keys = store.list_keys()
meta = store.get_metadata(key)
store.close()
```
