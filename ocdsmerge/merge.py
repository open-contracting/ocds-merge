import re
from collections import OrderedDict

import jsonref
import requests


class IdValue(str):
    """
    This is used to differentiate `id` values from other strings in `isinstance` checks.
    """
    def __init__(self, value):
        # Save the original value. For example, if the value is an integer, this attribute helps us to avoid coercing
        # the value to a string while merging.
        self.original_value = value
        str.__init__(value)


def get_latest_version():
    """
    Returns the tag of the latest version of OCDS.
    """
    return re.findall(r'\d+__\d+__\d+', requests.get('http://standard.open-contracting.org/schema/').text)[-1]


def get_latest_release_schema_url():
    """
    Returns the URL of the release schema in the latest version of OCDS.
    """
    return 'http://standard.open-contracting.org/schema/{}/release-schema.json'.format(get_latest_version())


def _get_types(value):
    if 'type' not in value:
        return []
    elif isinstance(value['type'], str):
        return [value['type']]
    else:
        return value['type']


def _get_merge_rules(properties, path=None):
    if path is None:
        path = ()

    for key, value in properties.items():
        new_path = path + (key,)
        types = _get_types(value)

        rules = {p for p in ('omitWhenMerged', 'versionId', 'wholeListMerge') if value.get(p)}

        if 'object' in types and 'properties' in value:
            yield from _get_merge_rules(value['properties'], path=new_path)
        if 'array' in types and 'items' in value:
            item_types = _get_types(value['items'])
            # Arrays that mix objects and non-objects are always wholeListMerge.
            if 'object' in item_types and any(t for t in item_types if t not in ('object', 'null')):
                rules.add('wholeListMerge')
            if 'object' in item_types and 'properties' in value['items']:
                yield from _get_merge_rules(value['items']['properties'], path=new_path)

        if rules:
            yield (new_path, rules)


def get_merge_rules(schema=None):
    schema = schema or get_latest_release_schema_url()
    if isinstance(schema, dict):
        deref_schema = jsonref.JsonRef.replace_refs(schema)
    elif schema.startswith('http'):
        deref_schema = jsonref.load_uri(schema)
    else:
        with open(schema) as f:
            deref_schema = jsonref.load(f)
    return dict(_get_merge_rules(deref_schema['properties']))


def flatten(obj, merge_rules=None, path=None, flattened=None):
    """
    Flatten any nested JSON object into simple key-value pairs. The key is the JSON path as a tuple. For example:

    {
        "a": "I am a",
        "b": ["A", "list"],
        "c": [
            {"ca": "I am ca"},
            {"cb": "I am cb"}
        ]
    }

    flattens to:

    {
        ('a',): 'I am a',
        ('b',): ['A', 'list'],
        ('c', 0, 'ca'): 'I am ca',
        ('c', 1, 'cb'): 'I am cb',
    }
    """
    if merge_rules is None:
        merge_rules = {}
    if path is None:
        path = ()
    if flattened is None:
        flattened = OrderedDict()

    if isinstance(obj, dict):
        iterable = obj.items()
        if not iterable:
            flattened[path] = {}
    else:
        iterable = enumerate(obj)
        if not iterable:
            flattened[path] = []

    for key, value in iterable:
        new_path = path + (key,)
        new_path_merge_rules = merge_rules.get(tuple(part for part in new_path if not isinstance(part, int)), [])

        if 'omitWhenMerged' in new_path_merge_rules:
            continue
        # If it is an array containing non-objects, or it is neither a list nor an object, or is is `wholeListMerge`.
        elif (isinstance(value, list) and any(not isinstance(item, dict) for item in value) or
                not isinstance(value, (dict, list)) or 'wholeListMerge' in new_path_merge_rules):
            flattened[new_path] = value
        else:
            flatten(value, merge_rules, new_path, flattened)

    return flattened


def unflatten(flattened):
    """
    Unflatten flattened object back into nested form.
    """
    unflattened = {}
    for flat_key in flattened:
        current_pos = unflattened
        for num, item in enumerate(flat_key):
            if isinstance(item, IdValue):
                if len(flat_key) - 1 == num:  # when this is an array of string or ints
                    current_pos.append(flattened[flat_key])
                else:
                    for obj in current_pos:
                        obj_id = obj.get('id')
                        if obj_id == item.original_value:
                            current_pos = obj
                            break
                    else:
                        new_pos = {"id": item.original_value}
                        current_pos.append(new_pos)
                        current_pos = new_pos
                continue
            new_pos = current_pos.get(item)
            if new_pos is not None:
                current_pos = new_pos
                continue
            if len(flat_key) - 1 == num:
                current_pos[item] = flattened[flat_key]
            elif isinstance(flat_key[num + 1], IdValue):
                new_pos = []
                current_pos[item] = new_pos
                current_pos = new_pos
            else:
                new_pos = {}
                current_pos[item] = new_pos
                current_pos = new_pos
    return unflattened


def process_flattened(flattened):
    """
    Replace numbers in json path (representing position in arrays)
    with special id object. This is to make detecting what is an
    array possible without needed to check schema.
    """
    # Keep ordered so that arrays will stay in the same order.
    processed = OrderedDict()
    for key in flattened:
        new_key = []
        for num, item in enumerate(key):
            if isinstance(item, int):
                id_value = flattened.get(tuple(key[:num + 1]) + ('id',))
                if id_value is None:
                    id_value = item
                new_key.append(IdValue(id_value))
                continue
            new_key.append(item)
        processed[tuple(new_key)] = flattened[key]
    return processed


def merge(releases, schema=None, merge_rules=None):
    """
    Takes a list of releases and merge them making a
    compiledRelease suitible for an OCDS Record
    """
    if not merge_rules:
        merge_rules = get_merge_rules(schema)
    merged = OrderedDict({("tag",): ['compiled']})
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        release.pop('tag', None)

        releaseID = release.pop("id")
        date = release.pop("date")

        flat = flatten(release, merge_rules)

        flat[("id",)] = releaseID
        flat[("date",)] = date

        processed = process_flattened(flat)
        # In flattening and adding the ids to the json path
        # we make sure each json path is going to same as long as
        # all the ids match. Position in the array is not relevent
        # (however it will keep this order anyway due to having an ordered dict).
        # This makes the actual merging come down to
        # just this statement.
        merged.update(processed)
    return unflatten(merged)


def merge_versioned(releases, schema=None, merge_rules=None):
    """
    Takes a list of releases and merge them making a
    versionedRelease suitible for an OCDS Record
    """
    if not merge_rules:
        merge_rules = get_merge_rules(schema)
    merged = OrderedDict()
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        ocid = release.pop("ocid")
        merged[("ocid",)] = ocid

        releaseID = release.pop("id")
        date = release.pop("date")
        tag = release.pop('tag', None)
        flat = flatten(release, merge_rules)

        processed = process_flattened(flat)

        for key, value in processed.items():
            new_value = {"releaseID": releaseID,
                         "releaseDate": date,
                         "releaseTag": tag,
                         "value": value}
            if key in merged:
                if value == merged[key][-1]['value']:
                    continue

            if key not in merged:
                merged[key] = []
            merged[key].append(new_value)

    return unflatten(merged)
