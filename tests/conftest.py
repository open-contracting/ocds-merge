import json
import os.path

import pytest

from ocdsmerge import Merger


@pytest.fixture
def simple_merger():
    with open(os.path.join('tests', 'fixtures', 'schema.json')) as f:
        return Merger(json.load(f))


@pytest.fixture
def empty_merger():
    return Merger({})
