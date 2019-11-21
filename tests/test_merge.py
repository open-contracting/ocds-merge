"""
It's possible to regenerate fixtures with commands like:

cat tests/fixtures/1.1/contextual.json | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    > tests/fixtures/1.1/contextual-compiled.json
cat tests/fixtures/1.1/contextual.json | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    --versioned > tests/fixtures/1.1/contextual-versioned.json
cat tests/fixtures/1.0/suppliers.json  | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    --versioned --schema https://standard.open-contracting.org/schema/1__0__3/release-schema.json \
    > tests/fixtures/1.0/suppliers-versioned.json
"""

import json
import os
import re
from collections import OrderedDict
from copy import deepcopy
from glob import glob

import pytest

from ocdsmerge import merge, merge_versioned
from ocdsmerge.merge import NonObjectReleaseError, MissingDateKeyError, NullDateValueError, NonStringDateValueError

from tests import tags, schema_url


with open(os.path.join('tests', 'fixtures', 'schema.json')) as f:
    simple_schema = json.load(f)

test_merge_argvalues = []
for minor_version, schema in (('1.1', None), ('1.1', schema_url), ('1.0', schema_url), ('schema', simple_schema)):
    if isinstance(schema, str):
        schema = schema.format(tags[minor_version])
    for suffix in ('compiled', 'versioned'):
        filenames = glob(os.path.join('tests', 'fixtures', minor_version, '*-{}.json'.format(suffix)))
        assert len(filenames), '{} fixtures not found'.format(suffix)
        test_merge_argvalues += [(filename, schema) for filename in filenames]


@pytest.mark.vcr()
@pytest.mark.parametrize('error, data', [
    (MissingDateKeyError, {}),
    (NullDateValueError, {'date': None}),
    (NonStringDateValueError, {'date': {}}),
    (NonObjectReleaseError, '{}'),
    (NonObjectReleaseError, b'{}'),
    (NonObjectReleaseError, []),
    (NonObjectReleaseError, tuple()),
    (NonObjectReleaseError, set()),
])
def test_errors(error, data):
    for method in (merge, merge_versioned):
        with pytest.raises(error):
            method([{'date': '2010-01-01'}, data])

    if not isinstance(data, dict):
        with pytest.raises(error):
            merge([data])
    else:
        release = deepcopy(data)

        expected = {
            'id': 'None-{}'.format(data.get('date')),
            'tag': ['compiled'],
        }

        if data.get('date') is not None:
            expected['date'] = data['date']

        assert merge([release]) == expected

    if not isinstance(data, dict):
        with pytest.raises(error):
            merge([data])
    else:
        release = deepcopy(data)
        release['initiationType'] = 'tender'

        expected = {
            'initiationType': [{
                'releaseID': None,
                'releaseDate': data.get('date'),
                'releaseTag': None,
                'value': 'tender',
            }],
        }

        assert merge_versioned([release]) == expected


@pytest.mark.vcr()
@pytest.mark.parametrize('filename,schema', test_merge_argvalues)
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


@pytest.mark.parametrize('i,j', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_merge_when_array_is_mixed(i, j):
    data = [{
        "ocid": "ocds-213czf-A",
        "id": "1",
        "date": "2000-01-01T00:00:00Z",
        "mixedArray": [
            {"id": 1},
            "foo"
        ]
    }, {
        "ocid": "ocds-213czf-A",
        "id": "2",
        "date": "2000-01-02T00:00:00Z",
        "mixedArray": [
            {"id": 2},
            "bar"
        ]
    }]

    output = OrderedDict([
        ('tag', ['compiled']),
        ('id', 'ocds-213czf-A-2000-01-02T00:00:00Z'),
        ('date', '2000-01-02T00:00:00Z'),
        ('ocid', 'ocds-213czf-A'),
        ('mixedArray', [
            {'id': 2},
            'bar',
        ]),
    ])

    assert merge(data, simple_schema) == output

    actual = deepcopy(data)
    expected = deepcopy(output)
    del actual[i]['mixedArray'][j]
    if i == 1:
        del expected['mixedArray'][j]

    assert merge(actual, simple_schema) == expected, 'removed item index {} from release index {}'.format(j, i)


@pytest.mark.parametrize('i,j', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_merge_when_array_is_mixed_without_schema(i, j):
    data = [{
        'ocid': 'ocds-213czf-A',
        "id": "1",
        "date": "2000-01-01T00:00:00Z",
        "mixedArray": [
            {"id": 1},
            "foo"
        ]
    }, {
        'ocid': 'ocds-213czf-A',
        "id": "2",
        "date": "2000-01-02T00:00:00Z",
        "mixedArray": [
            {"id": 2},
            "bar"
        ]
    }]

    output = OrderedDict([
        ('tag', ['compiled']),
        ('id', 'ocds-213czf-A-2000-01-02T00:00:00Z'),
        ('date', '2000-01-02T00:00:00Z'),
        ('ocid', 'ocds-213czf-A'),
        ('mixedArray', [
            {'id': 2},
            'bar',
        ]),
    ])

    assert merge(data, {}) == output

    actual = deepcopy(data)
    expected = deepcopy(output)
    del actual[i]['mixedArray'][j]
    if i == 1:
        del expected['mixedArray'][j]

    if j == 0:
        assert merge(actual, {}) == expected, 'removed item index {} from release index {}'.format(j, i)
    else:
        with pytest.raises(AssertionError):
            assert merge(actual, {}) == expected, 'removed item index {} from release index {}'.format(j, i)
