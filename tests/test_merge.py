import os
from glob import glob

import ocdsmerge
from tests import fixtures


def test_all():
    schema_url = 'http://standard.open-contracting.org/schema/1__1__2/release-schema.json'

    filenames = glob(os.path.join('tests', 'fixtures', '*.py'))
    assert len(filenames), 'fixtures not found'
    for filename in filenames:
        name = filename.split('/')[-1].split('.')[0]
        if name == "__init__":
            continue

        __import__("tests.fixtures." + name)
        fixture = getattr(fixtures, name)

        assert ocdsmerge.merge(fixture.releases) == fixture.compiledRelease, '{} compiledRelease differs'.format(name)
        assert ocdsmerge.merge(fixture.releases, schema_url) == fixture.compiledRelease, '{} compiledRelease with schema differs'.format(name)
        assert ocdsmerge.merge_versioned(fixture.releases) == fixture.versionedRelease, '{} versionedRelease differs'.format(name)
