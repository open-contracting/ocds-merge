import os
import warnings

import pytest

from ocdsmerge import APPEND, MERGE_BY_POSITION, merge
from ocdsmerge.merge import DuplicateIdValueWarning
from tests import load

releases = load(os.path.join('schema', 'identifier-merge-duplicate-id.json'))


def test_warn():
    fields = ['identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `{}` array"

    with pytest.warns(DuplicateIdValueWarning) as records:
        merge(releases)

    assert len(records) == 2

    for i, record in enumerate(records):
        message = string.format(fields[i])

        assert record.message.path == (fields[i],)
        assert record.message.id == '1'
        assert record.message.message == message
        assert str(record.message) == message


def test_raise():
    with pytest.raises(DuplicateIdValueWarning) as excinfo:
        with warnings.catch_warnings():
            warnings.filterwarnings('error', category=DuplicateIdValueWarning)
            merge(releases)

    message = "Multiple objects have the `id` value '1' in the `identifierMerge` array"

    assert excinfo.value.path == ('identifierMerge',)
    assert excinfo.value.id == '1'
    assert excinfo.value.message == message
    assert str(excinfo.value) == message


def test_ignore():
    with pytest.warns(None) as records:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)
            merge(releases)

    assert not records, 'unexpected warning: {}'.format(records[0].message)


def test_merge_by_position():
    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merge(releases + releases, rule_overrides={('array',): MERGE_BY_POSITION})

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))


def test_append():
    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merge(releases + releases, rule_overrides={('array',): APPEND})

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-append.json'))
