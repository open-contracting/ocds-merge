import json
import os
import warnings
from glob import glob

import pytest
from jsonschema import FormatChecker
from jsonschema.validators import Draft4Validator as validator

from tests import tags

schema_path = 'release-schema-{}.json'
versioned_release_schema_path = 'versioned-release-validation-schema-{}.json'

test_valid_argvalues = []
for minor_version, patch_tag in tags.items():
    filenames = glob(os.path.join('tests', 'fixtures', minor_version, '*.json'))
    assert len(filenames), 'ocds fixtures not found'
    for versioned, path in ((False, schema_path), (True, versioned_release_schema_path)):
        with open(os.path.join('tests', 'fixtures', path.format(patch_tag))) as f:
            schema = json.load(f)
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
            warnings.warn(json.dumps(error.instance, indent=2, separators=(',', ': ')))
            warnings.warn('{} ({})\n'.format(error.message, '/'.join(error.absolute_schema_path)))

    assert errors == 0, '{} is invalid. See warnings below.'.format(filename)
