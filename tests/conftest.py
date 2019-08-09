import pytest


@pytest.fixture
def vcr_cassette_name(request):
    return request.node.name.split('[', 1)[0]
