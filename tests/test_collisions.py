import os
import warnings

import pytest

from ocdsmerge import APPEND, MERGE_BY_POSITION, Merger
from ocdsmerge.exceptions import DuplicateIdValueWarning
from tests import load

releases = load(os.path.join('schema', 'identifier-merge-duplicate-id.json'))


@pytest.mark.vcr()
def test_warn(empty_merger):
    fields = ['identifierMerge', 'array']
    string = "Multiple objects have the `id` value '1' in the `nested.{}` array"

    with pytest.warns(DuplicateIdValueWarning) as records:
        empty_merger.create_compiled_release(releases)

    assert len(records) == 2

    for i, record in enumerate(records):
        message = string.format(fields[i])

        assert record.message.path == ('nested', fields[i],)
        assert record.message.id == '1'
        assert record.message.message == message
        assert str(record.message) == message


@pytest.mark.vcr()
def test_raise(empty_merger):
    with pytest.raises(DuplicateIdValueWarning) as excinfo:
        with warnings.catch_warnings():
            warnings.filterwarnings('error', category=DuplicateIdValueWarning)
            empty_merger.create_compiled_release(releases)

    message = "Multiple objects have the `id` value '1' in the `nested.identifierMerge` array"

    assert excinfo.value.path == ('nested', 'identifierMerge',)
    assert excinfo.value.id == '1'
    assert excinfo.value.message == message
    assert str(excinfo.value) == message


@pytest.mark.vcr()
def test_ignore(empty_merger):
    with pytest.warns(None) as records:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)
            empty_merger.create_compiled_release(releases)

    assert not records, 'unexpected warning: {}'.format(records[0].message)


@pytest.mark.vcr()
def test_merge_by_position():
    merger = Merger(rule_overrides={('nested', 'array',): MERGE_BY_POSITION})

    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))


@pytest.mark.vcr()
def test_append():
    merger = Merger(rule_overrides={('nested', 'array',): APPEND})

    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merger.create_compiled_release(releases + releases)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-append.json'))


@pytest.mark.vcr()
def test_append_no_id():
    merger = Merger(rule_overrides={('nested', 'array',): APPEND})
    data = load(os.path.join('schema', 'identifier-merge-no-id.json'))

    with pytest.warns(None) as records:
        with warnings.catch_warnings():
            compiled_release = merger.create_compiled_release(data + data)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-no-id-append.json'))
    assert not records, 'unexpected warning: {}'.format(records[0].message)
