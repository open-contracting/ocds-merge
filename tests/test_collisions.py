import os
import warnings

import pytest

from ocdsmerge import APPEND, MERGE_BY_POSITION, Merger
from ocdsmerge.exceptions import DuplicateIdValueWarning
from tests import load

releases = load(os.path.join('schema', 'identifier-merge-duplicate-id.json'))


def test_warn(empty_merger):
    fields = ['identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `nested.{}` array"

    with pytest.warns(DuplicateIdValueWarning) as records:
        empty_merger.create_compiled_release(releases)

    assert len(records) == 2

    for i, record in enumerate(records):
        assert str(record.message) == string.format(fields[i])


def test_raise(empty_merger):
    with warnings.catch_warnings():
        warnings.filterwarnings('error', category=DuplicateIdValueWarning)
        with pytest.raises(DuplicateIdValueWarning) as excinfo:
            empty_merger.create_compiled_release(releases)

    assert str(excinfo.value) == "Multiple objects have the `id` value '1' in the `nested.identifierMerge` array"


def test_ignore(empty_merger):
    with warnings.catch_warnings():
        warnings.simplefilter('error')  # no unexpected warnings

        warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)
        empty_merger.create_compiled_release(releases)


def test_merge_by_position():
    fields = ['identifierMerge', 'array', 'identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `nested.{}` array"

    merger = Merger(rule_overrides={('nested', 'array'): MERGE_BY_POSITION})

    with pytest.warns(DuplicateIdValueWarning) as records:
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))

    assert len(records) == 4

    for i, record in enumerate(records):
        assert str(record.message) == string.format(fields[i])


def test_append():
    fields = ['identifierMerge', 'array', 'identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `nested.{}` array"

    merger = Merger(rule_overrides={('nested', 'array'): APPEND})

    with pytest.warns(DuplicateIdValueWarning) as records:
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-append.json'))

    assert len(records) == 4

    for i, record in enumerate(records):
        assert str(record.message) == string.format(fields[i])


def test_append_no_id():
    merger = Merger(rule_overrides={('nested', 'array'): APPEND})
    data = load(os.path.join('schema', 'identifier-merge-no-id.json'))

    with warnings.catch_warnings():
        warnings.simplefilter('error')  # no unexpected warnings

        compiled_release = merger.create_compiled_release(data + data)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-no-id-append.json'))
