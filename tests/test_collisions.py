import os

import pytest

from ocdsmerge import merge, WARN, RAISE, APPEND, MERGE_BY_POSITION
from ocdsmerge.merge import DuplicateIdValueError, DuplicateIdValueWarning
from tests import load


releases = load(os.path.join('schema', 'identifier-merge-duplicate-id.json'))


def test_default():
    with pytest.warns(None) as record:
        merge(releases)
        assert not record, 'unexpected warning: {}'.format(record[0].message)


def test_warn():
    with pytest.warns(DuplicateIdValueWarning):
        merge(releases, collision_behavior=WARN)


def test_raise():
    with pytest.raises(DuplicateIdValueError) as excinfo:
        merge(releases, collision_behavior=RAISE)

    assert str(excinfo.value) == "Multiple objects have the `id` value '1' in the `identifierMerge` array"


def test_merge_by_position():
    with pytest.warns(None) as record:
        compiled_release = merge(releases + releases, rule_overrides={('array',): MERGE_BY_POSITION})
        assert not record, 'unexpected warning: {}'.format(record[0].message)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))


def test_append():
    with pytest.warns(None) as record:
        compiled_release = merge(releases + releases, rule_overrides={('array',): APPEND})
        assert not record, 'unexpected warning: {}'.format(record[0].message)

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-append.json'))


def test_mixed():
    with pytest.warns(DuplicateIdValueWarning):
        compiled_release = merge(releases + releases, collision_behavior=WARN,
                                 rule_overrides={('array',): MERGE_BY_POSITION})

    assert compiled_release == load(os.path.join('schema', 'identifier-merge-duplicate-id-by-position.json'))
