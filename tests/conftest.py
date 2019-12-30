import json
import os.path

import pytest

from ocdsmerge import Merger


@pytest.fixture()
def vcr_cassette_name(request):
    return request.node.name.split('[', 1)[0]


@pytest.fixture()
def simple_merger():
    with open(os.path.join('tests', 'fixtures', 'schema.json')) as f:
        return Merger(json.load(f))


@pytest.fixture()
def empty_merger():
    return Merger({})
