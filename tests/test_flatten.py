from ocdsmerge.flatten import flatten, process_flattened


def test_flatten():  # from documentation
    data = {
        "c": "I am a",
        "b": ["A", "list"],
        "a": [
            {"cb": "I am ca"},
            {"ca": "I am cb"}
        ]
    }

    assert flatten(data, {}) == {
        ('c',): 'I am a',
        ('b',): ['A', 'list'],
        ('a', 0, 'cb'): 'I am ca',
        ('a', 1, 'ca'): 'I am cb',
    }


def test_process_flattened():
    data = {
        "a": [
            {"id": "identifier"},
            {"key": "value"}
        ]
    }

    actual = process_flattened(flatten(data, {}), {})
    keys = list(actual.keys())
    values = list(actual.values())

    assert len(actual) == 2
    assert values == ['identifier', 'value']
    assert keys[0] == ('a', 'identifier', 'id')
    assert len(keys[1]) == 3
    assert keys[1][0] == 'a'
    assert len(keys[1][1]) == 36
    assert keys[1][2] == 'key'
