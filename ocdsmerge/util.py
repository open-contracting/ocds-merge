from __future__ import annotations

import re
from functools import lru_cache
from operator import itemgetter
from typing import Any

import requests

from ocdsmerge.exceptions import (
    MissingDateKeyError,
    NonObjectReleaseError,
    NonStringDateValueError,
    NullDateValueError,
)


@lru_cache
def get_tags() -> list[str]:
    """Return the tags of all versions of OCDS in alphabetical order."""
    response = requests.get('https://standard.open-contracting.org/schema/', timeout=10)
    response.raise_for_status()
    return re.findall(r'"(\d+__\d+__\d+)/', response.text)


def get_release_schema_url(tag: str) -> str:
    """Return the URL of the release schema in the given version of OCDS."""
    return f'https://standard.open-contracting.org/schema/{tag}/release-schema.json'


# If we need a method to get dates from releases, see https://github.com/open-contracting/ocds-merge/issues/25
def sorted_releases(releases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort a list of releases by date."""
    # Avoids an error if sorting a single compiled release.
    if isinstance(releases, list) and len(releases) == 1 and isinstance(releases[0], dict):
        return releases
    try:
        return sorted(releases, key=itemgetter('date'))
    except KeyError as e:
        raise MissingDateKeyError('date', 'The `date` field of at least one release is missing.') from e
    except TypeError as e:
        if ' not supported between instances of ' in e.args[0]:
            if 'NoneType' in e.args[0]:
                raise NullDateValueError('The `date` field of at least one release is null.') from e
            raise NonStringDateValueError('The `date` field of at least one release is not a string.') from e
        if e.args[0] in {
            'string indices must be integers',
            "string indices must be integers, not 'str'",
            'string index indices must be integers or slices, not str',
        }:
            raise NonObjectReleaseError(
                'At least one release is a string, not a dict. Use `json.loads` to parse the string as JSON.'
            ) from e
        if e.args[0] == 'byte indices must be integers or slices, not str':
            raise NonObjectReleaseError(
                'At least one release is a byte-string, not a dict. Use `json.loads` to parse the byte-string as JSON.'
            ) from e
        if e.args[0] == 'list indices must be integers or slices, not str':
            raise NonObjectReleaseError('At least one release is a list, not a dict.') from e
        if e.args[0] == 'tuple indices must be integers or slices, not str':
            raise NonObjectReleaseError('At least one release is a tuple, not a dict.') from e
        if e.args[0] in {"'set' object is not subscriptable", "'set' object is not subscriptable (key 'date')"}:
            raise NonObjectReleaseError('At least one release is a set, not a dict.') from e
        raise
