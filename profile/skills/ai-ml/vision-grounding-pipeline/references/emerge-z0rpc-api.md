# Emerge Z0RPC API Investigation Notes

## Executive Summary
Emerge node uses **Z0RPC (zerorpc)** over ZMQ for object storage. Objects are serialized with **dill** and require **inspectable source code** for custom classes. Plain dicts and built-in types cannot be stored directly.

## Connection
```python
import emerge
client = emerge.Client('localhost', 54242)  # host, port
# Or via ZMQ directly:
import zerorpc
client = zerorpc.Client()
client.connect('tcp://localhost:54242')
```

## Key Methods (via emerge.Client)

| Method | Purpose | Notes |
|--------|---------|-------|
| `client.store(obj)` | Store object | Requires `inspect.getsource(type(obj))` to work |
| `client.list(path)` | List directory | Returns list of object dicts |
| `client.getobject(path, nodill=False)` | Get single object | `nodill=True` returns raw dict |
| `client.search(field, query)` | Search by field | Field must be indexed |
| `client.mkdir(path)` | Create directory | Must exist before store |
| `client.rm(path)` | Remove object/dir | Recursive for dirs |

## Object Requirements
For `client.store(obj)` to work:
1. `obj` must be an instance of a **user-defined class** (not built-in)
2. The class must be **importable** by the emerge node server
3. Source code must be available via `inspect.getsource()`
4. Class is pickled with dill and sent to server

```python
# This FAILS:
client.store({"id": "test", "data": 123})  # TypeError: <class 'dict'> is built-in

# This WORKS (if class is importable on server):
class MyData:
    def __init__(self, id, data):
        self.id = id
        self.data = data

obj = MyData("test", 123)
obj.id = "test"      # Required: unique identifier
obj.path = "/mydata" # Required: storage path
obj.name = "mydata"  # Required: object name
client.store(obj)
```

## Server-Side Deserialization
In `emerge/node/server.py:746`:
```python
def store(self, obj):
    _obj = dill.loads(obj)  # obj is dill-serialized bytes
    # ... stores _obj in ZODB
```
The server must be able to import the class module. If not: `ModuleNotFoundError: No module named 'X'`

## Search/Query
- `client.search(field, value)` — exact match on indexed field
- `client.graphql(query)` — GraphQL queries (if enabled)
- No arbitrary query language exposed via emerge.Client

## Directory Structure
```
/                    # root
├── groundings/      # our target directory
├── warp/
├── unified/
├── test/
├── sms_vectors/
└── fleet/
```

## Current Blockers for Grounding Sync

1. **Custom class not importable on server**: `GroundingObject` defined in `/home/craig/tools/grounding_object.py` but emerge-node runs in different Python environment
2. **No HTTP/REST API**: Only Z0RPC/ZMQ
3. **CLI `update` command** doesn't accept file input for object creation

## Workaround Options

### Option A: Install class in emerge-node environment
```bash
# On server (where emerge-node runs):
pip install -e /path/to/package/containing/GroundingObject
# Or copy .py to site-packages
```

### Option B: Use zerorpc directly with dynamic class
```python
import zerorpc
import dill

client = zerorpc.Client()
client.connect('tcp://localhost:54242')

# Create class dynamically on both sides
class_def = '''
class GroundingObject:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
'''
exec(class_def)

obj = GroundingObject(id="test", path="/groundings", name="grounding", ...)
serialized = dill.dumps(obj)
# Need to send via raw Z0RPC call
```

### Option C: Use emerge's built-in types
Check if emerge has a generic "File" or "Document" type that accepts arbitrary JSON.

## Test Commands
```bash
# List root
emerge -h localhost:54242 ls /

# List groundings
emerge -h localhost:54242 ls /groundings

# Get object (nodill for raw dict)
python3 -c "import emerge; c=emerge.Client('localhost',54242); print(c.getobject('/groundings/test', True))"

# Search
python3 -c "import emerge; c=emerge.Client('localhost',54242); print(c.search('label', 'button'))"
```

## References
- Emerge source: `~/.local/lib/python3.13/site-packages/emerge/`
- zerorpc docs: https://github.com/0rpc/zerorpc-python
- dill serialization: https://dill.readthedocs.io/