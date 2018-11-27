import importlib
import os
from copy import deepcopy
from glob import glob

from ocdsmerge import merge, merge_versioned, get_merge_rules
from ocdsmerge.merge import get_latest_version, get_latest_release_schema_url, flatten

schema_url = 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'

schema = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "omitWhenMerged": True
        },
        "date": {
            "type": "string",
            "omitWhenMerged": True
        },
        "omitWhenMerged": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "omitWhenMerged": True
        },
        "keepWhenMerged": {
            "type": "string",
            "omitWhenMerged": False
        },
        "identifierMerge": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    }
                }
            },
            "wholeListMerge": False
        },
        "mixedArray": {
            "type": "array",
            "items": {
                "type": [
                    "object",
                    "string"
                ],
                "properties": {
                    "id": {
                        "type": "integer"
                    }
                }
            }
        }
    }
}


def test_merge():
    filenames = glob(os.path.join('tests', 'fixtures', '*_example.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        basename = os.path.splitext(os.path.basename(filename))[0]
        fixture = importlib.import_module('tests.fixtures.' + basename)

        assert fixture.compiledRelease == merge(fixture.releases), '{} merge differs'.format(basename)
        assert fixture.compiledRelease == merge(fixture.releases, schema_url), '{} merge with schema differs'.format(basename)  # noqa
        assert fixture.versionedRelease == merge_versioned(fixture.releases), '{} merge_versioned differs'.format(basename)  # noqa
        assert fixture.versionedRelease == merge_versioned(fixture.releases, schema_url), '{} merge_versioned with schema differs'.format(basename)  # noqa


def test_merge_when_merge_property_is_false():
    data = [{
        "id": "1",
        "date": "2000-01-01T00:00:00Z",
        "keepWhenMerged": "value",
        "identifierMerge": [
            {
                "id": 1
            }
        ]
    }, {
        "id": "2",
        "date": "2000-01-02T00:00:00Z",
        "keepWhenMerged": "value",
        "identifierMerge": [
            {
                "id": 2
            }
        ]
    }]

    assert merge(data, schema) == {
        'id': '2',
        'date': '2000-01-02T00:00:00Z',
        'tag': ['compiled'],
        'keepWhenMerged': 'value',
        'identifierMerge': [
            {'id': 1},
            {'id': 2},
        ],
    }


def test_merge_when_array_of_non_objects_is_omit_when_merged():
    data = [{
        "id": "1",
        "date": "2000-01-01T00:00:00Z",
        "omitWhenMerged": ["value"]
    }]

    assert merge(data, schema) == {
        'id': '1',
        'date': '2000-01-01T00:00:00Z',
        'tag': ['compiled'],
    }


def test_merge_when_array_is_mixed():
    data = [{
        "id": "1",
        "date": "2000-01-01T00:00:00Z",
        "mixedArray": [
            {"id": 1},
            "foo"
        ]
    }, {
        "id": "2",
        "date": "2000-01-02T00:00:00Z",
        "mixedArray": [
            {"id": 2},
            "bar"
        ]
    }]

    output = {
        'id': '2',
        'date': '2000-01-02T00:00:00Z',
        'tag': ['compiled'],
        'mixedArray': [
            {'id': 2},
            'bar',
        ],
    }

    assert merge(data, schema) == output

    for i in range(2):
        for j in range(2):
            actual = deepcopy(data)
            expected = deepcopy(output)
            del actual[i]['mixedArray'][j]
            if i == 1:
                del expected['mixedArray'][j]

            assert merge(actual, schema) == expected


def test_get_latest_version():
    assert get_latest_version() >= '1__1__3'


def test_get_latest_release_schema_url():
    assert get_latest_release_schema_url() >= 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'


def test_get_merge_rules():
    assert get_merge_rules(schema_url) == {
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('awards', 'items', 'unit', 'id'): {'versionId'},
        ('awards', 'suppliers', 'additionalIdentifiers'): {'wholeListMerge'},
        ('buyer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payee', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'items', 'unit', 'id'): {'versionId'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('parties', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'id'): {'versionId'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('tender', 'items', 'unit', 'id'): {'versionId'},
        ('tender', 'procuringEntity', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'tenderers', 'additionalIdentifiers'): {'wholeListMerge'},
    }


def test_flatten():
    data = {
        "a": "I am a",
        "b": ["A", "list"],
        "c": [
            {"ca": "I am ca"},
            {"cb": "I am cb"}
        ]
    }

    assert flatten(data) == {
        ('a',): 'I am a',
        ('b',): ['A', 'list'],
        ('c', 0, 'ca'): 'I am ca',
        ('c', 1, 'cb'): 'I am cb',
    }
