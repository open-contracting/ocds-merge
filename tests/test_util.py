from ocdsmerge.util import get_release_schema_url, get_tags


def test_get_release_schema_url():
    url = 'https://standard.open-contracting.org/schema/1__1__3/release-schema.json'
    assert get_release_schema_url('1__1__3') >= url


def test_get_tags():
    assert get_tags()[:11] == [
        '0__3__2',
        '0__3__3',
        '1__0__0',
        '1__0__1',
        '1__0__2',
        '1__0__3',
        '1__1__0',
        '1__1__1',
        '1__1__2',
        '1__1__3',
        '1__1__4',
    ]
