import json
import os.path
import re
import warnings
from copy import deepcopy
from glob import glob

import pytest

from ocdsmerge import CompiledRelease, Merger, VersionedRelease
from ocdsmerge.exceptions import (
    DuplicateIdValueWarning,
    InconsistentTypeError,
    MissingDateKeyError,
    NonObjectReleaseError,
    NonStringDateValueError,
    NullDateValueError,
)
from tests import load, path, schema_url, tags


def get_test_cases():
    test_merge_argvalues = []

    simple_schema = path('schema.json')

    for minor_version, schema in (('1.1', None), ('1.1', schema_url), ('1.0', schema_url), ('schema', simple_schema)):
        if schema and schema.startswith('http'):
            schema = schema.format(tags[minor_version])
        for suffix in ('compiled', 'versioned'):
            filenames = glob(path(os.path.join(minor_version, f'*-{suffix}.json')))
            assert len(filenames), f'{suffix} fixtures not found'
            test_merge_argvalues += [(filename, schema) for filename in filenames]

    return test_merge_argvalues


@pytest.mark.parametrize(('error', 'data'), [
    (MissingDateKeyError, {}),
    (NullDateValueError, {'date': None}),
    (NonStringDateValueError, {'date': {}}),
    (NonObjectReleaseError, '{}'),
    (NonObjectReleaseError, b'{}'),
    (NonObjectReleaseError, []),
    (NonObjectReleaseError, ()),
    (NonObjectReleaseError, set()),
])
def test_errors(error, data, empty_merger):
    for infix in ('compiled', 'versioned'):
        with pytest.raises(error):
            getattr(empty_merger, f'create_{infix}_release')([{'date': '2010-01-01'}, data])

    if not isinstance(data, dict):
        with pytest.raises(error):
            empty_merger.create_compiled_release([data])
    else:
        release = deepcopy(data)

        expected = {
            'id': f"None-{data.get('date')}",
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


def test_key_error(empty_merger):
    with pytest.raises(KeyError) as excinfo:
        empty_merger.create_compiled_release([{'date': '2010-01-01'}, {}])

    message = 'The `date` field of at least one release is missing.'

    assert excinfo.value.key == 'date'
    assert excinfo.value.message == message
    assert str(excinfo.value) == message


@pytest.mark.parametrize(('filename', 'schema'), get_test_cases())
def test_merge(filename, schema):
    merger = Merger(schema)

    infix = 'compiled' if filename.endswith('-compiled.json') else 'versioned'

    with open(filename) as f:
        expected = json.load(f)
    with open(re.sub(r'-(?:compiled|versioned)', '', filename)) as f:
        releases = json.load(f)

    original = deepcopy(releases)

    with warnings.catch_warnings():
        warnings.simplefilter('error')  # no unexpected warnings
        if filename == os.path.join('tests', 'fixtures', 'schema', 'identifier-merge-duplicate-id-compiled.json'):
            warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)

        actual = getattr(merger, f'create_{infix}_release')(releases)

    assert releases == original
    assert actual == expected, filename + '\n' + json.dumps(actual)


@pytest.mark.parametrize(('infix', 'cls'), [('compiled', CompiledRelease), ('versioned', VersionedRelease)])
def test_extend(infix, cls, empty_merger):
    expected = load(os.path.join('1.1', f'lists-{infix}.json'))
    releases = load(os.path.join('1.1', 'lists.json'))

    merged_release = getattr(empty_merger, f'create_{infix}_release')(releases[:1])

    merger = cls(merged_release, merge_rules=empty_merger.merge_rules)
    merger.extend(releases[1:])

    assert merger.asdict() == expected

    merger = cls(merged_release, schema={})
    merger.extend(releases[1:])

    assert merger.asdict() == expected


@pytest.mark.parametrize(('infix', 'cls'), [('compiled', CompiledRelease), ('versioned', VersionedRelease)])
def test_append(infix, cls, empty_merger):
    expected = load(os.path.join('1.1', f'lists-{infix}.json'))
    releases = load(os.path.join('1.1', 'lists.json'))

    merged_release = getattr(empty_merger, f'create_{infix}_release')(releases[:1])

    merger = cls(merged_release, merge_rules=empty_merger.merge_rules)
    merger.append(releases[1])

    assert merger.asdict() == expected

    merger = cls(merged_release, schema={})
    merger.append(releases[1])

    assert merger.asdict() == expected


@pytest.mark.parametrize(('value', 'infix'), [
    (1, '1'),
    ([1], '[1]'),
    ([{'object': 1}], "[{'object': 1}]")
])
def test_inconsistent_type_object_last(value, infix, empty_merger):
    data = [{
        "date": "2000-01-01T00:00:00Z",
        "integer": value
    }, {
        "date": "2000-01-02T00:00:00Z",
        "integer": {
            "object": 1
        }
    }]

    with pytest.raises(InconsistentTypeError) as excinfo:
        empty_merger.create_compiled_release(data)

    assert str(excinfo.value) == f"An earlier release had the value {infix} for /integer, but the current release has an object with a 'object' key"  # noqa: E501


def test_inconsistent_type_object_first(empty_merger):
    data = [{
        "date": "2000-01-01T00:00:00Z",
        "integer": {
            "object": 1
        }
    }, {
        "date": "2000-01-02T00:00:00Z",
        "integer": [
            {
                "object": 1
            }
        ]
    }]

    with pytest.raises(InconsistentTypeError) as excinfo:
        empty_merger.create_compiled_release(data)

    assert str(excinfo.value) == "An earlier release had the object {'object': 1} for /integer, but the current release has an array"  # noqa: E501


@pytest.mark.parametrize(('i', 'j'), [(0, 0), (0, 1), (1, 0), (1, 1)])
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
        f'removed item index {j} from release index {i}'


@pytest.mark.parametrize(('i', 'j'), [(0, 0), (0, 1), (1, 0), (1, 1)])
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
            f'removed item index {j} from release index {i}'
    else:
        with pytest.raises(AssertionError):
            assert empty_merger.create_compiled_release(actual) == expected, \
                f'removed item index {j} from release index {i}'
