from personio_py.mapping import MultiTagFieldMapping


def deserialize(value):
    return MultiTagFieldMapping('tags', 'tags').deserialize(value)


def test_deserialize_comma_separated():
    assert deserialize("AT Power-Point, CI/CD") == ["AT Power-Point", "CI/CD"]
    assert deserialize("single") == ["single"]


def test_deserialize_json_list_string():
    # Personio sometimes returns multi-select fields as a JSON-encoded list string
    assert deserialize('["AT Power-Point","CI/CD"]') == ["AT Power-Point", "CI/CD"]
    assert deserialize('["single"]') == ["single"]


def test_deserialize_empty():
    assert deserialize("") == []
    assert deserialize(None) == []


def test_serialize_roundtrip_comma_separated():
    mapping = MultiTagFieldMapping('tags', 'tags')
    assert mapping.serialize(["a", "b"]) == "a,b"
