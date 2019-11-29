import re
import uuid
import warnings
from collections import OrderedDict
from enum import Enum, auto, unique
from functools import lru_cache

import jsonref
import requests


@unique
class CollisionBehavior(Enum):
    RAISE = auto()
    WARN = auto()


@unique
class MergeStrategy(Enum):
    APPEND = auto()
    MERGE_BY_POSITION = auto()


globals().update(CollisionBehavior.__members__)
globals().update(MergeStrategy.__members__)


class IdValue(str):
    def __init__(self, identifier):
        self.identifier = identifier
        str.__init__(identifier)

    @property
    def original_value(self):
        return self._original_value

    @original_value.setter
    def original_value(self, original_value):
        self._original_value = original_value


class IdDict(OrderedDict):
    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier


class OCDSMergeError(Exception):
    """Base class for exceptions from within this package"""


class MissingDateKeyError(OCDSMergeError, KeyError):
    """Raised when a release is missing a 'date' key"""

    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __str__(self):
        return str(self.message)


class NonObjectReleaseError(OCDSMergeError, TypeError):
    """Raised when a release is not an object"""


class NullDateValueError(OCDSMergeError, TypeError):
    """Raised when a release has a null 'date' value"""


class NonStringDateValueError(OCDSMergeError, TypeError):
    """Raised when a release has a non-string 'date' value"""


class OCDSMergeWarning(UserWarning):
    """Base class for warnings from within this package"""


class DuplicateIdValueWarning(OCDSMergeWarning):
    """Used when at least two objects in the same array have the same value for the 'id' field"""

    def __init__(self, path, id, message):
        self.path = path
        self.id = id
        self.message = message

    def __str__(self):
        return str(self.message)


@lru_cache()
def get_tags():
    """
    Returns the tags of all versions of OCDS.
    """
    url = 'https://standard.open-contracting.org/schema/'
    return re.findall(r'"(\d+__\d+__\d+)/', requests.get(url).text)


def get_release_schema_url(tag):
    """
    Returns the URL of the release schema in the given version of OCDS.
    """
    return 'https://standard.open-contracting.org/schema/{}/release-schema.json'.format(tag)


def _get_types(prop):
    """
    Returns a property's `type` as a list.
    """
    if 'type' not in prop:
        return []
    if isinstance(prop['type'], str):
        return [prop['type']]
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

        # `omitWhenMerged` supersedes all other rules.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#omit-when-merged
        if value.get('omitWhenMerged') or value.get('mergeStrategy') == 'ocdsOmit':
            yield (new_path, {'omitWhenMerged'})
        # `wholeListMerge` supersedes any nested rules.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
        elif 'array' in types and (value.get('wholeListMerge') or value.get('mergeStrategy') == 'ocdsVersion'):
            yield (new_path, {'wholeListMerge'})
        elif 'object' in types and 'properties' in value:
            yield from _get_merge_rules(value['properties'], path=new_path)
        elif 'array' in types and 'items' in value:
            item_types = _get_types(value['items'])
            # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
            if any(item_type != 'object' for item_type in item_types):
                yield (new_path, {'wholeListMerge'})
            elif 'object' in item_types and 'properties' in value['items']:
                # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
                if 'id' not in value['items']['properties']:
                    yield (new_path, {'wholeListMerge'})
                else:
                    yield from _get_merge_rules(value['items']['properties'], path=new_path)

        # `versionId` merely assists in identifying `id` fields that are not on objects in arrays.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#versioned-data


@lru_cache()
def _get_merge_rules_from_url_or_path(schema):
    if schema.startswith('http'):
        return jsonref.load_uri(schema)
    with open(schema) as f:
        return jsonref.load(f)


def get_merge_rules(schema=None):
    """
    Returns merge rules as key-value pairs, in which the key is a JSON path as a tuple, and the value is a list of
    merge properties whose values are `true`.
    """
    schema = schema or get_release_schema_url(get_tags()[-1])
    if isinstance(schema, dict):
        deref_schema = jsonref.JsonRef.replace_refs(schema)
    else:
        deref_schema = _get_merge_rules_from_url_or_path(schema)
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
            flattened[path] = OrderedDict()
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
        # If it is neither an object nor an array, if it is `wholeListMerge`, or if it is an array containing
        # non-objects (even if `wholeListMerge` is `false`), use the whole list merge strategy.
        # Note: Behavior is undefined and inconsistent if the array is not in the schema and contains objects in some
        # cases but not in others.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
        elif (not isinstance(value, (dict, list)) or 'wholeListMerge' in new_path_merge_rules or
                isinstance(value, list) and any(not isinstance(item, dict) for item in value)):
            flattened[new_path] = value
        # Recurse into non-empty objects, and arrays of objects that aren't `wholeListMerge`.
        elif value:
            flatten(value, merge_rules, new_path, flattened)

    return flattened


def unflatten(processed, merge_rules):
    """
    Unflattens a processed object into a JSON object.
    """
    unflattened = OrderedDict()

    for key in processed:
        current_node = unflattened
        for end, part in enumerate(key, 1):
            # If this is a path to an item of an array.
            # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#identifier-merge
            if isinstance(part, IdValue):
                # If the `id` of an object in the array matches, change into it.
                for node in current_node:
                    if isinstance(node, IdDict) and node.identifier == part.identifier:
                        current_node = node
                        break
                # Otherwise, append a new object, and change into it.
                else:
                    new_node = IdDict()
                    new_node.identifier = part.identifier
                    # If the original object had an `id` value, set it.
                    if part.original_value is not None:
                        new_node['id'] = part.original_value
                    current_node.append(new_node)
                    current_node = new_node
                continue

            # Otherwise, this is a path to a property of an object.
            node = current_node.get(part)

            # If this is a path to a node we visited before, change into it. If it's an `id` field, it's already been
            # set to its original value.
            if node is not None:
                current_node = node
                continue

            # If this is a full path, copy the data.
            if len(key) == end:
                # Omit null'ed fields.
                if processed[key] is not None:
                    current_node[part] = processed[key]
                continue

            # If the path is to a new array, start a new array, and change into it.
            if isinstance(key[end], IdValue):
                new_node = []
            # If the path is to a new object, start a new object, and change into it.
            else:
                new_node = OrderedDict()

            current_node[part] = new_node
            current_node = new_node

    return unflattened


def process_flattened(flattened, rule_overrides=None):
    """
    Replace numbers in JSON paths (representing positions in arrays) with special objects. This ensures that objects
    in arrays with different `id` values have different JSON paths – and makes it easy to identify such arrays.
    """
    if rule_overrides is None:
        rule_overrides = {}

    # Keep arrays in order.
    processed = OrderedDict()

    # Cache identifiers, to avoid minting a new ID for each field of the same object.
    # e.g. {('awards', 0): '1', ('awards', 1): '2'}
    # This also tracks all identifiers of objects in each array, to warn about collisions.
    # e.g. {('awards',): {'1': 0, '2': 1}}
    identifiers = {}

    for key in flattened:
        new_key = []
        for end, part in enumerate(key, 1):
            # If this is a path to an item in an array.
            if isinstance(part, int):
                path = key[:end]
                if path in identifiers:
                    part = identifiers[path]
                else:
                    scope = path[:-1]

                    # If it is an array of objects, get the `id` value to apply the identifier merge strategy.
                    # https://standard.open-contracting.org/latest/en/schema/merging/#identifier-merge
                    id_value = flattened.get(path + ('id',))

                    # If the object contained no top-level `id` value, set a unique value.
                    if id_value is None:
                        identifier = uuid.uuid4()
                    else:
                        identifier = id_value

                    # Keep the integer index for the collision behavior.
                    index = part
                    # Keep the default `part`, so that we can issue warnings or raise errors later.
                    default = IdValue(identifier)

                    part = default
                    rule = rule_overrides.get(scope)
                    if rule == MergeStrategy.APPEND:
                        part = IdValue(uuid.uuid4())
                    elif rule == MergeStrategy.MERGE_BY_POSITION:
                        part = IdValue(index)

                    # Save the original value. (If the value is an integer, this avoids coercing it to a string.)
                    part.original_value = id_value

                    # Check whether the value is repeated in other objects in the array.
                    if scope not in identifiers:
                        identifiers[scope] = {}
                    if default not in identifiers[scope]:
                        identifiers[scope][default] = index
                    elif identifiers[scope][default] != index:
                        warnings.warn(DuplicateIdValueWarning(scope, default, 'Multiple objects have the `id` value '
                                      '{!r} in the `{}` array'.format(default, '.'.join(map(str, scope)))))

                    identifiers[path] = part
            new_key.append(part)
        processed[tuple(new_key)] = flattened[key]

    return processed


def sorted_releases(releases):
    """
    Sorts a list of releases by date.
    """
    if len(releases) == 1 and isinstance(releases[0], dict):
        return releases
    try:
        return sorted(releases, key=lambda release: release['date'])
    except KeyError:
        raise MissingDateKeyError('The `date` field of at least one release is missing.')
    except TypeError as e:
        if ' not supported between instances of ' in e.args[0]:
            if 'NoneType' in e.args[0]:
                raise NullDateValueError('The `date` field of at least one release is null.')
            else:
                raise NonStringDateValueError('The `date` field of at least one release is not a string.')
        elif e.args[0] == 'string indices must be integers':
            raise NonObjectReleaseError('At least one release is a string, not a dict. Use `json.loads` to parse the string as JSON.')  # noqa
        elif e.args[0] == 'byte indices must be integers or slices, not str':
            raise NonObjectReleaseError('At least one release is a byte-string, not a dict. Use `json.loads` to parse the byte-string as JSON.')  # noqa
        elif e.args[0] == 'list indices must be integers or slices, not str':
            raise NonObjectReleaseError('At least one release is a list, not a dict.')
        elif e.args[0] == 'tuple indices must be integers or slices, not str':
            raise NonObjectReleaseError('At least one release is a tuple, not a dict.')
        elif e.args[0] == "'set' object is not subscriptable":
            raise NonObjectReleaseError('At least one release is a set, not a dict.')
        else:
            raise


class Merger:
    def __init__(self, schema=None, merge_rules=None, rule_overrides=None):
        self.schema = schema
        self.merge_rules = merge_rules
        self.rule_overrides = rule_overrides

        if not schema:
            self.schema = get_release_schema_url(get_tags()[-1])
        if not merge_rules:
            self.merge_rules = get_merge_rules(schema)
        if not rule_overrides:
            self.rule_overrides = {}

    def create_compiled_release(self, releases):
        """
        Merges a list of releases into a compiledRelease.
        """
        merged = OrderedDict({('tag',): ['compiled']})
        return self._create_merged_release(add_release_to_compiled_release, releases, merged)

    def create_versioned_release(self, releases):
        """
        Merges a list of releases into a versionedRelease.
        """
        merged = OrderedDict()
        return self._create_merged_release(add_release_to_versioned_release, releases, merged)

    def _create_merged_release(self, merge_method, releases, merged):
        for release in sorted_releases(releases):
            merge_method(release, merged, self.merge_rules, self.rule_overrides)

        return unflatten(merged, self.merge_rules)


def merge(releases, schema=None, merge_rules=None, rule_overrides=None):
    """
    Merges a list of releases into a compiledRelease.
    """
    merger = Merger(schema, merge_rules, rule_overrides)
    return merger.create_compiled_release(releases)


def merge_versioned(releases, schema=None, merge_rules=None, rule_overrides=None):
    """
    Merges a list of releases into a versionedRelease.
    """
    merger = Merger(schema, merge_rules, rule_overrides)
    return merger.create_versioned_release(releases)


def add_release_to_compiled_release(release, merged, merge_rules, rule_overrides=None):
    """
    Merges one release into a compiledRelease.
    """
    release = release.copy()

    # `ocid` and `date` are required fields, but the data can be invalid.
    ocid = release.get('ocid')
    date = release.get('date')
    # Prior to OCDS 1.1.4, `tag` didn't set "omitWhenMerged": true.
    release.pop('tag', None)  # becomes ["compiled"]

    flat = flatten(release, merge_rules)
    processed = process_flattened(flat, rule_overrides)

    # Add an `id` and `date`.
    merged[('id',)] = '{}-{}'.format(ocid, date)
    merged[('date',)] = date

    # In OCDS 1.0, `ocid` incorrectly sets "mergeStrategy": "ocdsOmit".
    merged[('ocid',)] = ocid

    merged.update(processed)


def add_release_to_versioned_release(release, merged, merge_rules, rule_overrides=None):
    """
    Merges one release into a versionedRelease.
    """
    release = release.copy()

    # Don't version the OCID.
    ocid = release.pop('ocid', None)
    merged[('ocid',)] = ocid

    # `id` and `date` are required fields, but the data can be invalid.
    releaseID = release.get('id')
    date = release.get('date')
    # Prior to OCDS 1.1.4, `tag` didn't set "omitWhenMerged": true.
    tag = release.pop('tag', None)

    flat = flatten(release, merge_rules)
    processed = process_flattened(flat, rule_overrides)

    for key, value in processed.items():
        # If value is unchanged, don't add to history.
        if key in merged and value == merged[key][-1]['value']:
            continue

        if key not in merged:
            merged[key] = []

        merged[key].append(OrderedDict([
            ('releaseID', releaseID),
            ('releaseDate', date),
            ('releaseTag', tag),
            ('value', value),
        ]))
