import json
import os.path
import re
from copy import deepcopy
from glob import glob

import pytest

from ocdsmerge import CompiledRelease, Merger, VersionedRelease
from ocdsmerge.exceptions import (MissingDateKeyError, NonObjectReleaseError, NonStringDateValueError,
                                  NullDateValueError)
from tests import load, path, schema_url, tags

simple_schema = load('schema.json')

test_merge_argvalues = []
for minor_version, schema in (('1.1', None), ('1.1', schema_url), ('1.0', schema_url), ('schema', simple_schema)):
    if isinstance(schema, str):
        schema = schema.format(tags[minor_version])
    for suffix in ('compiled', 'versioned'):
        filenames = glob(path(os.path.join(minor_version, '*-{}.json'.format(suffix))))
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
def test_errors(error, data, empty_merger):
    for infix in ('compiled', 'versioned'):
        with pytest.raises(error):
            getattr(empty_merger, 'create_{}_release'.format(infix))([{'date': '2010-01-01'}, data])

    if not isinstance(data, dict):
        with pytest.raises(error):
            empty_merger.create_compiled_release([data])
    else:
        release = deepcopy(data)

        expected = {
            'id': 'None-{}'.format(data.get('date')),
            'tag': ['compiled'],
        }

        if data.get('date') is not None:
            expected['date'] = data['date']

        assert empty_merger.create_compiled_release([release]) == expected

    if not isinstance(data, dict):
        with pytest.raises(error):
            empty_merger.create_versioned_release([data])
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

        assert empty_merger.create_versioned_release([release]) == expected


@pytest.mark.vcr()
@pytest.mark.parametrize('filename,schema', test_merge_argvalues)
def test_merge(filename, schema):
    merger = Merger(schema)

    if filename.endswith('-compiled.json'):
        infix = 'compiled'
    else:
        infix = 'versioned'

    with open(filename) as f:
        expected = json.load(f)
    with open(re.sub(r'-(?:compiled|versioned)', '', filename)) as f:
        releases = json.load(f)

    original = deepcopy(releases)
    actual = getattr(merger, 'create_{}_release'.format(infix))(releases)

    assert releases == original
    assert actual == expected, filename + '\n' + json.dumps(actual)


@pytest.mark.vcr()
@pytest.mark.parametrize('infix,cls', [('compiled', CompiledRelease), ('versioned', VersionedRelease)])
def test_extend(infix, cls, empty_merger):
    releases = load(os.path.join('1.1', 'lists.json'))

    merged_release = getattr(empty_merger, 'create_{}_release'.format(infix))(releases[:1])

    merger = cls(merged_release, merge_rules=empty_merger.merge_rules)
    merger.extend(releases[1:])

    expected = load(os.path.join('1.1', 'lists-{}.json'.format(infix)))

    assert merger.asdict() == expected


@pytest.mark.vcr()
@pytest.mark.parametrize('infix,cls', [('compiled', CompiledRelease), ('versioned', VersionedRelease)])
def test_append(infix, cls, empty_merger):
    releases = load(os.path.join('1.1', 'lists.json'))

    merged_release = getattr(empty_merger, 'create_{}_release'.format(infix))(releases[:1])

    merger = cls(merged_release, merge_rules=empty_merger.merge_rules)
    merger.append(releases[1])

    expected = load(os.path.join('1.1', 'lists-{}.json'.format(infix)))

    assert merger.asdict() == expected


@pytest.mark.parametrize('i,j', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_merge_when_array_is_mixed(i, j, simple_merger):
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

    output = {
        'tag': ['compiled'],
        'id': 'ocds-213czf-A-2000-01-02T00:00:00Z',
        'date': '2000-01-02T00:00:00Z',
        'ocid': 'ocds-213czf-A',
        'mixedArray': [
            {'id': 2},
            'bar',
        ],
    }

    assert simple_merger.create_compiled_release(data) == output

    actual = deepcopy(data)
    expected = deepcopy(output)
    del actual[i]['mixedArray'][j]
    if i == 1:
        del expected['mixedArray'][j]

    assert simple_merger.create_compiled_release(actual) == expected, \
        'removed item index {} from release index {}'.format(j, i)


@pytest.mark.parametrize('i,j', [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_merge_when_array_is_mixed_without_schema(i, j, empty_merger):
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

    output = {
        'tag': ['compiled'],
        'id': 'ocds-213czf-A-2000-01-02T00:00:00Z',
        'date': '2000-01-02T00:00:00Z',
        'ocid': 'ocds-213czf-A',
        'mixedArray': [
            {'id': 2},
            'bar',
        ],
    }

    assert empty_merger.create_compiled_release(data) == output

    actual = deepcopy(data)
    expected = deepcopy(output)
    del actual[i]['mixedArray'][j]
    if i == 1:
        del expected['mixedArray'][j]

    if j == 0:
        assert empty_merger.create_compiled_release(actual) == expected, \
            'removed item index {} from release index {}'.format(j, i)
    else:
        with pytest.raises(AssertionError):
            assert empty_merger.create_compiled_release(actual) == expected, \
                'removed item index {} from release index {}'.format(j, i)
