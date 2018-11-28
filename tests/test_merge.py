import json
import os
import re
from collections import OrderedDict
from copy import deepcopy
from glob import glob

import pytest

from ocdsmerge import merge, merge_versioned, get_merge_rules
from ocdsmerge.merge import get_latest_version, get_latest_release_schema_url, flatten, process_flattened

schema_url = 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'

with open(os.path.join('tests', 'fixtures', 'schema.json')) as f:
    simple_schema = json.load(f)

argvalues = []
for directory, schemas in (('ocds', (None, schema_url)), ('schema', (simple_schema,))):
    for schema in schemas:
        for suffix in ('compiled', 'versioned'):
            filenames = glob(os.path.join('tests', 'fixtures', directory, '*-{}.json'.format(suffix)))
            # assert len(filenames), '{} fixtures not found'.format(suffix)
            argvalues += [(filename, schema) for filename in filenames]


@pytest.mark.parametrize('filename,schema', argvalues)
def test_merge(filename, schema):
    if filename.endswith('-compiled.json'):
        method = merge
    else:
        method = merge_versioned

    with open(filename) as f:
        expected = json.load(f, object_pairs_hook=OrderedDict)
    with open(re.sub(r'-(?:compiled|versioned)', '', filename)) as f:
        releases = json.load(f, object_pairs_hook=OrderedDict)

    original = deepcopy(releases)

    assert method(releases, schema) == expected, filename + '\n' + json.dumps(method(releases, schema))
    assert releases == original


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

    assert merge(data, simple_schema) == output

    for i in range(2):
        for j in range(2):
            actual = deepcopy(data)
            expected = deepcopy(output)
            del actual[i]['mixedArray'][j]
            if i == 1:
                del expected['mixedArray'][j]

            assert merge(actual, simple_schema) == expected, 'removed item index {} from release index {}'.format(j, i)


def test_merge_when_array_is_mixed_without_schema():
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

    assert merge(data, {}) == output

    for i in range(2):
        for j in range(2):
            actual = deepcopy(data)
            expected = deepcopy(output)
            del actual[i]['mixedArray'][j]
            if i == 1:
                del expected['mixedArray'][j]

            if j == 0:
                assert merge(actual, {}) == expected, 'removed item index {} from release index {}'.format(j, i)
            else:
                with pytest.raises((AttributeError, AssertionError)):
                    assert merge(actual, {}) == expected, 'removed item index {} from release index {}'.format(j, i)


def test_get_latest_version():
    assert get_latest_version() >= '1__1__3'


def test_get_latest_release_schema_url():
    assert get_latest_release_schema_url() >= 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'


def test_get_merge_rules():
    assert get_merge_rules(schema_url) == {
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('awards', 'items', 'unit', 'id'): {'versionId'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'items', 'unit', 'id'): {'versionId'},
        ('contracts', 'relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('parties', 'additionalIdentifiers'): {'wholeListMerge'},
        ('parties', 'roles'): {'wholeListMerge'},
        ('relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('tag',): {'wholeListMerge'},
        ('tender', 'additionalProcurementCategories'): {'wholeListMerge'},
        ('tender', 'id'): {'versionId'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('tender', 'items', 'unit', 'id'): {'versionId'},
        ('tender', 'submissionMethod'): {'wholeListMerge'},

        # Deprecated
        ('awards', 'amendment', 'changes'): {'wholeListMerge'},
        ('awards', 'amendments', 'changes'): {'wholeListMerge'},
        ('awards', 'suppliers', 'additionalIdentifiers'): {'wholeListMerge'},
        ('buyer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'amendment', 'changes'): {'wholeListMerge'},
        ('contracts', 'amendments', 'changes'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payee', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'implementation', 'transactions', 'payer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'amendment', 'changes'): {'wholeListMerge'},
        ('tender', 'amendments', 'changes'): {'wholeListMerge'},
        ('tender', 'procuringEntity', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'tenderers', 'additionalIdentifiers'): {'wholeListMerge'},
    }


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

    assert process_flattened(flatten(data)) == {
        ('a', 'identifier', 'id'): 'identifier',
        ('a', '1', 'key'): 'value',
    }
