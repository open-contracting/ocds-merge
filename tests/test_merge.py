import importlib
import os
from glob import glob

import pytest

from ocdsmerge import merge, merge_versioned
from ocdsmerge.merge import get_latest_release_schema_url, get_merge_rules

schema_url = 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'


def test_all():
    filenames = glob(os.path.join('tests', 'fixtures', '*_example.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        basename = os.path.splitext(os.path.basename(filename))[0]
        fixture = importlib.import_module('tests.fixtures.' + basename)

        assert fixture.compiledRelease == merge(fixture.releases), '{} merge differs'.format(basename)
        assert fixture.compiledRelease == merge(fixture.releases, schema_url), '{} merge with schema differs'.format(basename)  # noqa
        assert fixture.versionedRelease == merge_versioned(fixture.releases), '{} merge_versioned differs'.format(basename)  # noqa
        assert fixture.versionedRelease == merge_versioned(fixture.releases, schema_url), '{} merge_versioned with schema differs'.format(basename)  # noqa


@pytest.mark.skip(reason=get_latest_release_schema_url())
def test_get_latest_release_schema_url():
    pass  # to display the return value when running `pytest -rs`


def test_get_merge_rules():
    assert get_merge_rules(schema_url) == {
        ('awards', 'items', 'additionalClassifications'): ['wholeListMerge'],
        ('awards', 'items', 'unit', 'id'): ['versionId'],
        ('awards', 'suppliers', 'additionalIdentifiers'): ['wholeListMerge'],
        ('buyer', 'additionalIdentifiers'): ['wholeListMerge'],
        ('contracts', 'implementation', 'transactions', 'payee', 'additionalIdentifiers'): ['wholeListMerge'],
        ('contracts', 'implementation', 'transactions', 'payer', 'additionalIdentifiers'): ['wholeListMerge'],
        ('contracts', 'items', 'additionalClassifications'): ['wholeListMerge'],
        ('contracts', 'items', 'unit', 'id'): ['versionId'],
        ('date',): ['omitWhenMerged'],
        ('id',): ['omitWhenMerged'],
        ('parties', 'additionalIdentifiers'): ['wholeListMerge'],
        ('tender', 'id'): ['versionId'],
        ('tender', 'items', 'additionalClassifications'): ['wholeListMerge'],
        ('tender', 'items', 'unit', 'id'): ['versionId'],
        ('tender', 'procuringEntity', 'additionalIdentifiers'): ['wholeListMerge'],
        ('tender', 'tenderers', 'additionalIdentifiers'): ['wholeListMerge'],
    }


def test_merge_if_merge_property_is_false():
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
            }
        }
    }



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
