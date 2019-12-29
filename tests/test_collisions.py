import os
import warnings

import pytest

from ocdsmerge import APPEND, MERGE_BY_POSITION, Merger
from ocdsmerge.errors import DuplicateIdValueWarning
from tests import load

releases = load(os.path.join('schema', 'identifier-merge-duplicate-id.json'))
merger = Merger()


def test_warn():
    fields = ['identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `{}` array"

    with pytest.warns(DuplicateIdValueWarning) as records:
        merger.create_compiled_release(releases)

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
            merger.create_compiled_release(releases)

    message = "Multiple objects have the `id` value '1' in the `identifierMerge` array"

    assert excinfo.value.path == ('identifierMerge',)
    assert excinfo.value.id == '1'
    assert excinfo.value.message == message
    assert str(excinfo.value) == message


def test_ignore():
    with pytest.warns(None) as records:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)
            merger.create_compiled_release(releases)

    assert not records, 'unexpected warning: {}'.format(records[0].message)


def test_merge_by_position():
    merger = Merger(rule_overrides={('array',): MERGE_BY_POSITION})

    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))


def test_append():
    merger = Merger(rule_overrides={('array',): APPEND})

    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-append.json'))
