import importlib
import os
from glob import glob

import ocdsmerge


def test_all():
    schema = 'http://standard.open-contracting.org/schema/1__1__3/release-schema.json'

    filenames = glob(os.path.join('tests', 'fixtures', '*_example.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        basename = os.path.splitext(os.path.basename(filename))[0]
        fixture = importlib.import_module('tests.fixtures.' + basename)

        assert fixture.compiledRelease == ocdsmerge.merge(fixture.releases), '{} merge differs'.format(basename)
        assert fixture.compiledRelease == ocdsmerge.merge(fixture.releases, schema), '{} merge with schema differs'.format(basename)  # noqa
        assert fixture.versionedRelease == ocdsmerge.merge_versioned(fixture.releases), '{} merge_versioned differs'.format(basename)  # noqa
        assert fixture.versionedRelease == ocdsmerge.merge_versioned(fixture.releases, schema), '{} merge_versioned with schema differs'.format(basename)  # noqa
