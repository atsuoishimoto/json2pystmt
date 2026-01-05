# json2pystmt

Convert JSON to Python assignment statements. Useful for grepping JSON, diffing JSON objects, and debugging.

## Installation

```bash
pip install json2pystmt
```

Or with uv:

```bash
uv add json2pystmt
```

## Command Line Usage

```bash
# From file
json2pystmt data.json

# From stdin
cat data.json | json2pystmt

# Custom root variable name
json2pystmt -r myvar data.json
```

### Example

Input JSON:
```json
{"key1": [1, 2, {"x": {"y": "z"}}]}
```

Output:
```python
root = {}
root['key1'] = [None] * 3
root['key1'][0] = 1
root['key1'][1] = 2
root['key1'][2] = {}
root['key1'][2]['x'] = {}
root['key1'][2]['x']['y'] = 'z'
```

### Use Cases

**Grep for values in JSON:**
```bash
json2pystmt data.json | grep "error"
```

**Diff two JSON files:**
```bash
diff <(json2pystmt a.json) <(json2pystmt b.json)
```

## Library Usage

```python
from json2pystmt import json2pystmt

data = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
lines = json2pystmt(data)
for line in lines:
    print(line)
```

Output:
```python
root = {}
root['users'] = [None] * 2
root['users'][0] = {}
root['users'][0]['name'] = 'Alice'
root['users'][1] = {}
root['users'][1]['name'] = 'Bob'
```

### API

#### `json2pystmt(jsonobj, rootname="root")`

Convert a JSON-compatible object to a list of Python assignment statements.

- `jsonobj`: Any JSON-compatible Python object (dict, list, str, int, float, bool, None)
- `rootname`: Variable name to use as the root (default: `"root"`)
- Returns: List of assignment statement strings

## Requirements

- Python 3.10+

## License

MIT
