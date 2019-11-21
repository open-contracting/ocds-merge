import json
import os.path

tags = {
    '1.0': '1__0__3',
    '1.1': '1__1__4',
}

schema_url = 'https://standard.open-contracting.org/schema/{}/release-schema.json'


def path(filename):
    return os.path.join('tests', 'fixtures', filename)


def read(filename, mode='rt', encoding=None, **kwargs):
    with open(path(filename), mode, encoding=encoding, **kwargs) as f:
        return f.read()


def load(*args, **kwargs):
    return json.loads(read(*args, **kwargs))
