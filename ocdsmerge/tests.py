import unittest
import ocdsmerge.merge as merge
import ocdsmerge.fixtures as fixtures
import os

import glob

class TestAllFixtures(unittest.TestCase):
    maxDiff = None
    def test_all(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for file_name in glob.glob(os.path.join(current_dir, 'fixtures', '*.py')):
            name = file_name.split('/')[-1].split('.')[0]
            if name == "__init__":
                continue
            
            __import__("ocdsmerge.fixtures." + name)
            fixture = getattr(fixtures, name)

            self.assertEqual(merge.merge(fixture.releases),
                             fixture.compiledRelease,
                             'Test compiled for ' + name)

            self.assertEqual(merge.merge_versioned(fixture.releases),
                             fixture.versionedRelease,
                             'Test versioned for ' + name)


if __name__ == '__main__':
    unittest.main()
