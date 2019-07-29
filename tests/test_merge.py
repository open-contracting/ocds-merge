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
import warnings
from collections import OrderedDict
from copy import deepcopy
from glob import glob

import pytest
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator as validator

from ocdsmerge import merge, merge_versioned, get_merge_rules
from ocdsmerge.merge import (get_tags, get_release_schema_url, flatten, process_flattened, MissingDateKeyError,
                             NullDateValueError)

tags = {
    '1.0': '1__0__3',
    '1.1': '1__1__4',
}

schema_url = 'https://standard.open-contracting.org/schema/{}/release-schema.json'
versioned_release_schema_url = 'https://standard.open-contracting.org/schema/{}/versioned-release-validation-schema.json'  # noqa
schema_path = 'release-schema-{}.json'
versioned_release_schema_path = 'versioned-release-validation-schema-{}.json'

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

test_valid_argvalues = []
for minor_version, patch_tag in tags.items():
    filenames = glob(os.path.join('tests', 'fixtures', minor_version, '*.json'))
    assert len(filenames), 'ocds fixtures not found'
    for versioned, path in ((False, schema_path), (True, versioned_release_schema_path)):
        with open(os.path.join('tests', 'fixtures', path.format(patch_tag))) as f:
            schema = json.load(f)
        for filename in filenames:
            if not versioned ^ filename.endswith('-versioned.json'):
                test_valid_argvalues.append((filename, schema))


def custom_warning_formatter(message, category, filename, lineno, line=None):
    return str(message).replace(os.getcwd() + os.sep, '')


warnings.formatwarning = custom_warning_formatter


@pytest.mark.vcr()
@pytest.mark.parametrize('error, data', [(MissingDateKeyError, {}), (NullDateValueError, {'date': None})])
def test_date_errors(error, data):
    for method in (merge, merge_versioned):
        with pytest.raises(error):
            method([{'date': '2010-01-01'}, data])

    release = deepcopy(data)
    assert merge([release]) == {
        'id': 'None-None',
        'tag': ['compiled'],
    }

    release = deepcopy(data)
    release['initiationType'] = 'tender'
    assert merge_versioned([release]) == {
        'initiationType': [{
            'releaseID': None,
            'releaseDate': None,
            'releaseTag': None,
            'value': 'tender',
        }],
    }


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


def test_get_tags():
    assert get_tags()[:12] == [
        '0__3__2',
        '0__3__2',
        '0__3__3',
        '0__3__3',
        '1__0__0',
        '1__0__0',
        '1__0__1',
        '1__0__1',
        '1__0__2',
        '1__0__2',
        '1__0__3',
        '1__0__3',
    ]


def test_get_release_schema_url():
    assert get_release_schema_url('1__1__3') >= 'https://standard.open-contracting.org/schema/1__1__3/release-schema.json'  # noqa


def test_get_merge_rules_1_1():
    assert get_merge_rules(schema_url.format(tags['1.1'])) == {
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('contracts', 'relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('parties', 'additionalIdentifiers'): {'wholeListMerge'},
        ('parties', 'roles'): {'wholeListMerge'},
        ('relatedProcesses', 'relationship'): {'wholeListMerge'},
        ('tag',): {'omitWhenMerged'},
        ('tender', 'additionalProcurementCategories'): {'wholeListMerge'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
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


def test_get_merge_rules_1_0():
    assert get_merge_rules(schema_url.format(tags['1.0'])) == {
        ('awards', 'amendment', 'changes'): {'wholeListMerge'},
        ('awards', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('awards', 'suppliers'): {'wholeListMerge'},
        ('buyer', 'additionalIdentifiers'): {'wholeListMerge'},
        ('contracts', 'amendment', 'changes'): {'wholeListMerge'},
        ('contracts', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('date',): {'omitWhenMerged'},
        ('id',): {'omitWhenMerged'},
        ('ocid',): {'omitWhenMerged'},
        ('tag',): {'omitWhenMerged'},
        ('tender', 'amendment', 'changes'): {'wholeListMerge'},
        ('tender', 'items', 'additionalClassifications'): {'wholeListMerge'},
        ('tender', 'procuringEntity', 'additionalIdentifiers'): {'wholeListMerge'},
        ('tender', 'submissionMethod'): {'wholeListMerge'},
        ('tender', 'tenderers'): {'wholeListMerge'},
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


@pytest.mark.parametrize('filename,schema', test_valid_argvalues)
def test_valid(filename, schema):
    errors = 0

    with open(filename) as f:
        data = json.load(f)
    if filename.endswith('-versioned.json') or filename.endswith('-compiled.json'):
        data = [data]

    for datum in data:
        for error in validator(schema, format_checker=FormatChecker()).iter_errors(datum):
            errors += 1
            warnings.warn(json.dumps(error.instance, indent=2, separators=(',', ': ')))
            warnings.warn('{} ({})\n'.format(error.message, '/'.join(error.absolute_schema_path)))

    assert errors == 0, '{} is invalid. See warnings below.'.format(filename)
