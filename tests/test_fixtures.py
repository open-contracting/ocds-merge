"""
It's possible to regenerate fixtures with commands like:

cat tests/fixtures/1.1/contextual.json | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    > tests/fixtures/1.1/contextual-compiled.json
cat tests/fixtures/1.1/contextual.json | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    --versioned > tests/fixtures/1.1/contextual-versioned.json
cat tests/fixtures/1.0/suppliers.json  | jq -crM .[] | ocdskit package-releases | ocdskit --pretty compile \
    --versioned --schema https://standard.open-contracting.org/schema/1__0__3/release-schema.json \
    > tests/fixtures/1.0/suppliers-versioned.json
"""

import json
import os
import warnings
from glob import glob

import pytest
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator as validator

from tests import load, path, tags

release_schema_path = 'release-schema-{}.json'
versioned_release_schema_path = 'versioned-release-validation-schema-{}.json'

test_valid_argvalues = []
for minor_version, patch_tag in tags.items():
    filenames = glob(path(os.path.join(minor_version, '*.json')))
    assert len(filenames), 'ocds fixtures not found'
    for versioned, schema_path in ((False, release_schema_path), (True, versioned_release_schema_path)):
        schema = load(schema_path.format(patch_tag))
        for filename in filenames:
            if not versioned ^ filename.endswith('-versioned.json'):
                test_valid_argvalues.append((filename, schema))


def custom_warning_formatter(message, category, filename, lineno, line=None):
    return str(message).replace(os.getcwd() + os.sep, '')


warnings.formatwarning = custom_warning_formatter


@pytest.mark.parametrize('filename,schema', test_valid_argvalues)
def test_valid(filename, schema):
    errors = 0

    with open(filename) as f:
        data = json.load(f)
    if filename.endswith('-versioned.json') or filename.endswith('-compiled.json'):
        data = [data]

    for datum in data:
        for error in validator(schema, format_checker=FormatChecker()).iter_errors(datum):
            errors += 1
            warnings.warn(json.dumps(error.instance, indent=2))
            warnings.warn('{} ({})\n'.format(error.message, '/'.join(error.absolute_schema_path)))

    assert errors == 0, '{} is invalid. See warnings below.'.format(filename)
