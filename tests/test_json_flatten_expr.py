from json2pystmt import build_json_expr_lines, json2pystmt


def test_nested_dict_with_list():
    data = {"key1": [1, 2, 3, {"x": {"y": "z"}}]}
    result = build_json_expr_lines(data)
    assert result == [
        "root = {}",
        "root['key1'] = [None] * 4",
        "root['key1'][0] = 1",
        "root['key1'][1] = 2",
        "root['key1'][2] = 3",
        "root['key1'][3] = {}",
        "root['key1'][3]['x'] = {}",
        "root['key1'][3]['x']['y'] = 'z'",
    ]

def test_simple_dict():
    data = {"a": 1, "b": 2}
    result = build_json_expr_lines(data)
    assert result == [
        "root = {}",
        "root['a'] = 1",
        "root['b'] = 2",
    ]

def test_simple_list():
    data = [1, 2, 3]
    result = build_json_expr_lines(data)
    assert result == [
        "root = [None] * 3",
        "root[0] = 1",
        "root[1] = 2",
        "root[2] = 3",
    ]

def test_empty_dict():
    data = {}
    result = build_json_expr_lines(data)
    assert result == "{}"

def test_empty_list():
    data = []
    result = build_json_expr_lines(data)
    assert result == "[]"

def test_custom_rootname():
    data = {"key": "value"}
    result = build_json_expr_lines(data, rootname="data")
    assert result == [
        "data = {}",
        "data['key'] = 'value'",
    ]

def test_null_value():
    data = "null"
    result = build_json_expr_lines(data)
    assert result == ["root = None"]

def test_string_value():
    data = "hello"
    result = build_json_expr_lines(data)
    assert result == ["root = 'hello'"]

def test_number_value():
    data = 42
    result = build_json_expr_lines(data)
    assert result == ["root = 42"]

def test_nested_empty_structures():
    data = {"a": [], "b": {}}
    result = build_json_expr_lines(data)
    assert result == [
        "root = {}",
        "root['a'] = []",
        "root['b'] = {}",
    ]


def test_alias_function():
    data = {"key": "value"}
    assert json2pystmt(data) == build_json_expr_lines(data)

def test_alias_with_rootname():
    data = {"key": "value"}
    assert json2pystmt(data, "obj") == build_json_expr_lines(data, "obj")
