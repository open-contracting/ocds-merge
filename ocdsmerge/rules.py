from functools import lru_cache

import jsonref

from ocdsmerge.util import get_release_schema_url, get_tags


def get_merge_rules(schema=None):
    """
    Returns merge rules as key-value pairs, in which the key is a JSON path as a tuple, and the value is a list of
    merge properties whose values are `true`.
    """
    schema = schema or get_release_schema_url(get_tags()[-1])
    if isinstance(schema, dict):
        return _get_merge_rules_from_dereferenced_schema(jsonref.JsonRef.replace_refs(schema))
    else:
        return _get_merge_rules_from_url_or_path(schema)


@lru_cache()
def _get_merge_rules_from_url_or_path(schema):
    if schema.startswith('http'):
        deref_schema = jsonref.load_uri(schema)
    else:
        with open(schema) as f:
            deref_schema = jsonref.load(f)
    return _get_merge_rules_from_dereferenced_schema(deref_schema)


def _get_merge_rules_from_dereferenced_schema(deref_schema):
    return dict(_get_merge_rules(deref_schema['properties']))


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

        # `omitWhenMerged` supersedes all other rules.
        # See https://standard.open-contracting.org/1.1/en/schema/merging/#discarded-fields
        if value.get('omitWhenMerged') or value.get('mergeStrategy') == 'ocdsOmit':
            yield new_path, {'omitWhenMerged'}
        # `wholeListMerge` supersedes any nested rules.
        # See https://standard.open-contracting.org/1.1/en/schema/merging/#whole-list-merge
        elif 'array' in types and (value.get('wholeListMerge') or value.get('mergeStrategy') == 'ocdsVersion'):
            yield new_path, {'wholeListMerge'}
        # See https://standard.open-contracting.org/1.1/en/schema/merging/#object-values
        elif 'object' in types and 'properties' in value:
            yield from _get_merge_rules(value['properties'], path=new_path)
        # See https://standard.open-contracting.org/1.1/en/schema/merging/#whole-list-merge
        elif 'array' in types and 'items' in value:
            item_types = _get_types(value['items'])
            if any(item_type != 'object' for item_type in item_types):
                yield new_path, {'wholeListMerge'}
            elif 'object' in item_types and 'properties' in value['items']:
                if 'id' not in value['items']['properties']:
                    yield new_path, {'wholeListMerge'}
                else:
                    yield from _get_merge_rules(value['items']['properties'], path=new_path)


def _get_types(prop):
    """
    Returns a property's `type` as a list.
    """
    if 'type' not in prop:
        return []
    if isinstance(prop['type'], str):
        return [prop['type']]
    return prop['type']
