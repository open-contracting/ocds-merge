import importlib
import os
from glob import glob

import pytest

import ocdsmerge
from ocdsmerge.merge import get_latest_release_schema_url, get_merge_rules

schema = 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'


def test_all():
    filenames = glob(os.path.join('tests', 'fixtures', '*_example.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        basename = os.path.splitext(os.path.basename(filename))[0]
        fixture = importlib.import_module('tests.fixtures.' + basename)

        assert fixture.compiledRelease == ocdsmerge.merge(fixture.releases), '{} merge differs'.format(basename)
        assert fixture.compiledRelease == ocdsmerge.merge(fixture.releases, schema), '{} merge with schema differs'.format(basename)  # noqa
        assert fixture.versionedRelease == ocdsmerge.merge_versioned(fixture.releases), '{} merge_versioned differs'.format(basename)  # noqa
        assert fixture.versionedRelease == ocdsmerge.merge_versioned(fixture.releases, schema), '{} merge_versioned with schema differs'.format(basename)  # noqa


@pytest.mark.skip(reason=get_latest_release_schema_url())
def test_get_latest_release_schema_url():
    pass  # to display the return value when running `pytest -rs`


def test_get_merge_rules():
    assert get_merge_rules(schema) == {
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
