import warnings
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


def _get_merge_rules(properties, path):
    for key, value in properties.items():
        # All fields with merge rules must have a `type`.
        prop_type = value.get('type')
        if not prop_type:
            continue

        new_path = path + (key,)

        rules = [p for p in ('omitWhenMerged', 'versionId', 'wholeListMerge') if p in value]
        if rules:
            yield (new_path, rules)

        if 'object' in prop_type and 'properties' in value:
            yield from _get_merge_rules(value['properties'], path=new_path)
        if 'array' in prop_type and 'items' in value:
            item_type = value['items'].get('type')
            if 'object' in item_type and 'properties' in value['items']:
                yield from _get_merge_rules(value['items']['properties'], path=new_path)


def get_merge_rules(schema=None):
    schema = schema or get_latest_release_schema_url()
    if isinstance(schema, dict):
        deref_schema = jsonref.JsonRef.replace_refs(schema)
    elif schema.startswith('http'):
        deref_schema = jsonref.load_uri(schema)
    else:
        with open(schema) as f:
            deref_schema = jsonref.load(f)
    return dict(_get_merge_rules(deref_schema['properties'], tuple()))


def remove_number_path(path):
    return tuple(item for item in path if not isinstance(item, int))


def flatten(path, flattened, obj, merge_rules):
    """
    Flatten any nested json object into simple key value pairs.
    The key is the json path represented as a tuple.
    eg. {"a": "I am a", "b": ["A", "list"], "c": [{"ca": "I am ca"}, {"cb": "I am cb"}]}
    will flatten to
    {('a',): 'I am a',
     ('b', 1): 'list',
     ('c', 0, 'ca'): 'I am ca',
     ('b', 0): 'A',
     ('c', 1, 'cb'): 'I am cb'}
    """
    if isinstance(obj, dict):
        iterable = list(obj.items())
        if not iterable:
            flattened[path] = {}
    else:
        iterable = list(enumerate(obj))
        if not iterable:
            flattened[path] = []
    for key, value in iterable:
        new_path = path + (key,)

        # Unless it is a list of objects, the list should be treated and merged as a whole entity. Such lists include
        # lists of: strings, ints, floats, and lists (which occur, for example, in GeoJSON fields).
        if isinstance(value, list) and value and not isinstance(value[0], dict):
            flattened[new_path] = value
        elif isinstance(value, (dict, list)) and 'wholeListMerge' not in merge_rules.get(remove_number_path(new_path), []):  # noqa
            flatten(new_path, flattened, value, merge_rules)
        elif 'omitWhenMerged' in merge_rules.get(remove_number_path(new_path), []):
            continue
        else:
            flattened[new_path] = value
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

        flat = flatten((), OrderedDict(), release, merge_rules)

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
        flat = flatten((), OrderedDict(), release, merge_rules)

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
