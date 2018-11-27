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


def _get_types(prop):
    """
    Returns a property's `type` as a list.
    """
    if 'type' not in prop:
        return []
    elif isinstance(prop['type'], str):
        return [prop['type']]
    else:
        return prop['type']


def _get_merge_rules(properties, path=None):
    """
    Yields merge rules as key-value pairs, in which the first element is a JSON path as a tuple, and the second element
    is a list of merge properties whose values are `true`.
    """
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
            # Arrays containing non-objects use the whole list merge strategy (even if `wholeListMerge` is `false`).
            # See http://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
            if 'object' in item_types and any(t for t in item_types if t != 'object'):
                rules.add('wholeListMerge')
            if 'object' in item_types and 'properties' in value['items']:
                yield from _get_merge_rules(value['items']['properties'], path=new_path)

        if rules:
            yield (new_path, rules)


def get_merge_rules(schema=None):
    """
    Returns merge rules as key-value pairs, in which the key is a JSON path as a tuple, and the value is a list of
    merge properties whose values are `true`.
    """
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
    Flattens a JSON object into key-value pairs, in which the key is the JSON path as a tuple. For example:

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
        # Remove array indices to find the merge rule for this JSON path in the data.
        new_path_merge_rules = merge_rules.get(tuple(part for part in new_path if not isinstance(part, int)), [])

        if 'omitWhenMerged' in new_path_merge_rules:
            continue
        # If it is neither an object nor an array, if it is `wholeListMerge`, or if it is an array containing non-objects
        # (even if `wholeListMerge` is `false`), use the whole list merge strategy.
        # See http://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
        # See http://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
        elif (not isinstance(value, (dict, list)) or 'wholeListMerge' in new_path_merge_rules or
                isinstance(value, list) and any(not isinstance(item, dict) for item in value)):
            flattened[new_path] = value
        # Recurse into objects, and arrays of objects that aren't `wholeListMerge`.
        else:
            flatten(value, merge_rules, new_path, flattened)

    return flattened


def unflatten(flattened):
    """
    Unflattens a flattend object into a JSON object.
    """
    unflattened = {}

    for key in flattened:
        current_pos = unflattened
        for end, part in enumerate(key, 1):
            # If this is a path to an item in an array.
            if isinstance(part, IdValue):
                for obj in current_pos:
                    obj_id = obj.get('id')
                    if obj_id == part.original_value:
                        current_pos = obj
                        break
                else:
                    new_pos = {'id': part.original_value}
                    current_pos.append(new_pos)
                    current_pos = new_pos
                continue

            new_pos = current_pos.get(part)
            # True if this is a partial path to an array of objects or a path to an `id` field in an array of objects.
            if new_pos is not None:
                current_pos = new_pos
                continue

            # If this is a full path, copy the data.
            if len(key) == end:
                current_pos[part] = flattened[key]
            # If the partial path is a new array, start a new array, and change into it.
            elif isinstance(key[end], IdValue):
                new_array = []
                current_pos[part] = new_array
                current_pos = new_array
            # If the partial path is a new object, start a new object, and change into it.
            else:
                new_object = {}
                current_pos[part] = new_object
                current_pos = new_object

    return unflattened


def process_flattened(flattened):
    """
    Replace numbers in JSON path (representing position in arrays) with special id objects. This is to make detecting
    what is an array possible without needed to check schema.
    """
    # Keep arrays in order.
    processed = OrderedDict()
    for key in flattened:
        new_key = []
        for end, part in enumerate(key, 1):
            # If this is a path to an item in an array.
            if isinstance(part, int):
                # If it is an array of objects, get the `id` value to apply the identifier merge strategy.
                # http://standard.open-contracting.org/latest/en/schema/merging/#identifier-merge
                id_value = flattened.get(tuple(key[:end]) + ('id',))
                # If the objects contain no top-level `id` values, the whole list merge strategy is used.
                # http://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
                if id_value is None:
                    id_value = part
                part = IdValue(id_value)
            new_key.append(part)
        processed[tuple(new_key)] = flattened[key]
    return processed


def merge(releases, schema=None, merge_rules=None):
    """
    Merges a list of releases into a compiledRelease.
    """
    if not merge_rules:
        merge_rules = get_merge_rules(schema)

    merged = OrderedDict({('tag',): ['compiled']})
    for release in sorted(releases, key=lambda rel: rel['date']):
        release = release.copy()

        releaseID = release.pop('id')
        date = release.pop('date')
        release.pop('tag', None)
        flat = flatten(release, merge_rules)

        flat[('id',)] = releaseID
        flat[('date',)] = date

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
    Merges a list of releases into a versionedRelease.
    """
    if not merge_rules:
        merge_rules = get_merge_rules(schema)

    merged = OrderedDict()
    for release in sorted(releases, key=lambda rel: rel['date']):
        release = release.copy()

        ocid = release.pop('ocid')
        merged[('ocid',)] = ocid

        releaseID = release.pop('id')
        date = release.pop('date')
        tag = release.pop('tag', None)
        flat = flatten(release, merge_rules)

        processed = process_flattened(flat)

        for key, value in processed.items():
            new_value = {
                'releaseID': releaseID,
                'releaseDate': date,
                'releaseTag': tag,
                'value': value,
            }
            if key in merged:
                if value == merged[key][-1]['value']:
                    continue

            if key not in merged:
                merged[key] = []
            merged[key].append(new_value)

    return unflatten(merged)
