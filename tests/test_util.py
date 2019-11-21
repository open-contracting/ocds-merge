from ocdsmerge.merge import get_release_schema_url, get_tags, flatten, process_flattened


def test_get_release_schema_url():
    assert get_release_schema_url('1__1__3') >= 'https://standard.open-contracting.org/schema/1__1__3/release-schema.json'  # noqa


def test_get_tags():
    assert get_tags()[:11] == [
        '0__3__2',
        '0__3__3',
        '1__0__0',
        '1__0__1',
        '1__0__2',
        '1__0__3',
        '1__1__0',
        '1__1__1',
        '1__1__2',
        '1__1__3',
        '1__1__4',
    ]


def test_flatten():  # from documentation
    data = {
        "c": "I am a",
        "b": ["A", "list"],
        "a": [
            {"cb": "I am ca"},
            {"ca": "I am cb"}
        ]
    }

    assert flatten(data) == {
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

    actual = process_flattened(flatten(data))
    keys = list(actual.keys())
    values = list(actual.values())

    assert len(actual) == 2
    assert values == ['identifier', 'value']
    assert keys[0] == ('a', 'identifier', 'id')
    assert len(keys[1]) == 3
    assert keys[1][0] == 'a'
    assert len(keys[1][1]) == 36
    assert keys[1][2] == 'key'
