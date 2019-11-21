import json
import os
import warnings

import pytest

from ocdsmerge import merge, WARN, RAISE, IGNORE
from ocdsmerge.merge import DuplicateIdValueError, DuplicateIdValueWarning
from tests import read


def custom_warning_formatter(message, category, filename, lineno, line=None):
    return '{}: {}'.format(category.__name__, str(message).replace(os.getcwd() + os.sep, ''))


warnings.formatwarning = custom_warning_formatter
releases = json.loads(read(os.path.join('schema', 'identifier-merge-duplicate-id.json')))

def test_default():
    with pytest.warns(DuplicateIdValueWarning):
        merge(releases)


def test_warn():
    with pytest.warns(DuplicateIdValueWarning):
        merge(releases, collision_behavior=WARN)


def test_ignore():
    with pytest.warns(None) as record:
        merge(releases, collision_behavior=IGNORE)
        assert not record, 'unexpected warning: {}'.format(record[0].message)


def test_raise():
    with pytest.raises(DuplicateIdValueError) as excinfo:
        merge(releases, collision_behavior=RAISE)

    assert str(excinfo.value) == "Multiple objects have the `id` value '1' in the `identifierMerge` array"
