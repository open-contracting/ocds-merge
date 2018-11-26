import importlib
import os
from glob import glob

import ocdsmerge
from tests import fixtures


def test_all():
    schema_url = 'http://standard.open-contracting.org/schema/1__1__2/release-schema.json'

    filenames = glob(os.path.join('tests', 'fixtures', '*_example.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        basename = os.path.splitext(os.path.basename(filename))[0]
        fixture = importlib.import_module('tests.fixtures.' + basename)

        assert ocdsmerge.merge(fixture.releases) == fixture.compiledRelease, '{} merge differs'.format(basename)
        assert ocdsmerge.merge(fixture.releases, schema_url) == fixture.compiledRelease, '{} merge with schema differs'.format(basename)  # noqa
        assert ocdsmerge.merge_versioned(fixture.releases) == fixture.versionedRelease, '{} merge_versioned differs'.format(basename)  # noqa
