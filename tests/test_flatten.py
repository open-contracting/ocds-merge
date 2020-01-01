from ocdsmerge.flatten import flatten


def test_flatten_1():  # from documentation
    data = {
        "c": "I am a",
        "b": ["A", "list"],
        "a": [
            {"id": 1, "cb": "I am ca"},
            {"id": 2, "ca": "I am cb"}
        ]
    }

    assert flatten(data, {}, {}, {}) == {
        ('c',): 'I am a',
        ('b',): ['A', 'list'],
        ('a', '1', 'cb'): 'I am ca',
        ('a', '1', 'id'): 1,
        ('a', '2', 'ca'): 'I am cb',
        ('a', '2', 'id'): 2,
    }


def test_flatten_2():
    data = {
        "a": [
            {"id": "identifier"},
            {"key": "value"}
        ]
    }

    actual = flatten(data, {}, {}, {})
    keys = list(actual.keys())
    values = list(actual.values())

    assert len(actual) == 2
    assert values == ['identifier', 'value']
    assert keys[0] == ('a', 'identifier', 'id')
    assert len(keys[1]) == 3
    assert keys[1][0] == 'a'
    assert len(keys[1][1]) == 36
    assert keys[1][2] == 'key'
