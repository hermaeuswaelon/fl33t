# emerge — Distributed Object Filesystem

**Version**: 0.0.5 · **Author**: Darren Govoni (Elasticode) · **License**: MIT
**Source**: `https://github.com/radiantone/emerge`
**Local**: `~/.local/bin/emerge` (PATH), `~/.emerge/data/` (store), `emerge.ini` (config)

## Architecture

emerge is a ZeroRPC/ZMQ-based distributed object filesystem backed by ZODB/BTrees:

- **Objects**: Python objects serialized via `dill`, stored in ZODB `OOBTree`
- **RPC**: ZeroRPC client/server — `Z0RPCClient` connects to `NodeServer` via TCP
- **Broker**: Requires `BROKER` env var pointing to a broker host (port 5558) — or runs in standalone mode
- **GraphQL**: Built-in schema generation via `graphene` — each object class gets auto-generated queries
- **Filesystem**: POSIX-like paths (`/`, `mkdir`, `ls`, `cp`, `rm`, `cat`) with typed entries (file, directory, reference, node)

## CLI Commands
```
emerge init               → create emerge.ini config
emerge ls /               → list root directory
emerge ls -l /path        → long listing
emerge mkdir /path        → create directory
emerge cp /src /dst       → copy object
emerge rm /path           → remove object
emerge cat /path          → display object contents
emerge search field query → search objects by field
emerge query /path        → run object's query method
emerge graphql "{...}"    → GraphQL query
emerge call /path method  → call object method
emerge code /path         → list source code
emerge methods /path      → list available methods
emerge node start         → start node server (needs BROKER env)
```

## Local Use (no broker)
Without a broker, `emerge ls /` and `emerge cat /path` return empty results. The local data dir at `~/.emerge/data/` is ready for standalone ZODB-backed use via direct Python API (see `sms-persist-bridge` for the same ZODB pattern).

## Integration Points
- ZODB persistence layer (shared with SMS persistence bridge)
- Object store for VSA vector metadata and conversation snapshots
- GraphQL query interface for structured data retrieval
