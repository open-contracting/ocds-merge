import uuid
import warnings
from enum import Enum, auto, unique

from ocdsmerge.errors import DuplicateIdValueWarning

VERSIONED_VALUE_KEYS = frozenset(['releaseID', 'releaseDate', 'releaseTag', 'value'])


@unique
class MergeStrategy(Enum):
    APPEND = auto()
    MERGE_BY_POSITION = auto()


globals().update(MergeStrategy.__members__)


class IdValue(str):
    """
    A string with ``identifier`` and ``original_value`` properties.
    """
    def __init__(self, identifier):
        self.identifier = identifier
        str.__init__(identifier)

    @property
    def original_value(self):
        return self._original_value

    @original_value.setter
    def original_value(self, original_value):
        self._original_value = original_value


class IdDict(dict):
    """
    A dictionary with an ``identifier`` property.
    """
    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier


def is_versioned_value(value):
    """
    Returns whether the value is a versioned value.
    """
    return len(value) == 4 and VERSIONED_VALUE_KEYS.issuperset(value)


def flatten(obj, merge_rules, rule_overrides, path=None, rule_path=None, flattened=None):
    """
    Flattens a JSON object into key-value pairs, in which the key is the JSON path as a tuple. For example:

    Replaces numbers in JSON paths (representing positions in arrays) with special objects. This ensures that objects
    in arrays with different `id` values have different JSON paths – and makes it easy to identify such arrays.

    .. code:: json

       {
           "a": "I am a",
           "b": ["A", "list"],
           "c": [
               {"id": 1, "cb": "I am ca"},
               {"id": 2, "ca": "I am cb"}
           ]
       }

    flattens to:

    .. code:: python

       {
           ('a',): 'I am a',
           ('b',): ['A', 'list'],
           ('a', '1', 'cb'): 'I am ca',
           ('a', '1', 'id'): 1,
           ('a', '2', 'ca'): 'I am cb',
           ('a', '2', 'id'): 2,
       }
    """
    if path is None:
        path = ()
    if flattened is None:
        flattened = {}
    if rule_path is None:
        rule_path = ()

    if isinstance(obj, dict):
        iterable = obj.items()
        if not iterable:
            flattened[path] = {}
    else:
        iterable = enumerate(obj)
        if not iterable:
            flattened[path] = []

    # This tracks the identifiers of objects in an array, to warn about collisions.
    # e.g. {('awards',): {'1': 0, '2': 1}}
    identifiers = {}

    for key, value in iterable:
        if type(key) is int:
            new_key, default_key = _id_value(key, value, rule_overrides.get(rule_path))

            # Check whether the value is repeated in other objects in the array.
            default_path = path + (default_key,)
            if default_path not in identifiers:
                identifiers[default_path] = key
            elif identifiers[default_path] != key:
                warnings.warn(DuplicateIdValueWarning(rule_path, default_key, 'Multiple objects have the `id` '
                              'value {!r} in the `{}` array'.format(default_key, '.'.join(map(str, rule_path)))))

            new_rule_path = rule_path
            new_path = path + (new_key,)
        else:
            new_rule_path = rule_path + (key,)
            new_path = path + (key,)

        # Remove array indices to find the merge rule for this JSON path in the data.
        new_path_merge_rules = merge_rules.get(new_rule_path, set())

        if 'omitWhenMerged' in new_path_merge_rules:
            continue
        # If it's neither an object nor an array, if it's `wholeListMerge`, if it's an array containing non-objects
        # (even if `wholeListMerge` is `false`), or if it's versioned values, use the whole list merge strategy.
        # Note: Behavior is undefined and inconsistent if the array is not in the schema and contains objects in some
        # cases but not in others.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
        elif not isinstance(value, (dict, list)) or 'wholeListMerge' in new_path_merge_rules or \
                type(value) is list and any(not isinstance(item, dict) for item in value) or \
                len(value) and all(is_versioned_value(item) for item in value):
            flattened[new_path] = value
        # Recurse into non-empty objects, and arrays of objects that aren't `wholeListMerge`.
        elif value:
            flatten(value, merge_rules, rule_overrides, new_path, new_rule_path, flattened)

    return flattened


def _id_value(key, value, rule):
    # If it is an array of objects, get the `id` value to apply the identifier merge strategy.
    # https://standard.open-contracting.org/latest/en/schema/merging/#identifier-merge
    if 'id' in value:
        id_value = value['id']
        identifier = id_value
    # If the object contained no top-level `id` value, set a unique value.
    else:
        id_value = None
        identifier = str(uuid.uuid1(1))  # use 1 instead of MAC address

    # Calculate the default key for the warning.
    default_key = IdValue(identifier)

    if rule == MergeStrategy.APPEND:
        if 'id' in value:
            new_key = IdValue(str(uuid.uuid1(1)))
        else:  # avoid creating an extra UUID
            new_key = default_key
    elif rule == MergeStrategy.MERGE_BY_POSITION:
        new_key = IdValue(key)
    else:
        new_key = default_key

    # Save the original value. (If the value is an integer, this avoids coercing it to a string.)
    new_key.original_value = id_value

    return new_key, default_key


def unflatten(processed):
    """
    Unflattens a processed object into a JSON object.
    """
    unflattened = {}

    identifiers = {}

    for key in processed:
        current_node = unflattened

        for end, part in enumerate(key, 1):
            # If this is a path to an item of an array.
            # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#identifier-merge
            if type(part) is IdValue:
                path = key[:end]

                # If the `id` of an object in the array matches, change into it.
                id_path = path + (part.identifier,)
                if id_path in identifiers:
                    current_node = identifiers[id_path]

                # Otherwise, append a new object, and change into it.
                else:
                    new_node = IdDict()
                    new_node.identifier = part.identifier

                    # If the original object had an `id` value, set it.
                    if part.original_value is not None:
                        new_node['id'] = part.original_value

                    # Cache which identifiers appear in which arrays.
                    identifiers[path + (new_node.identifier,)] = new_node

                    current_node.append(new_node)
                    current_node = new_node

                continue

            # Otherwise, this is a path to a property of an object. If this is a path to a node we visited before,
            # change into it. If it's an `id` field, it's already been set to its original value.
            if part in current_node:
                current_node = current_node[part]
                continue

            if end < len(key):
                # If the path is to a new array, start a new array, and change into it.
                if type(key[end]) is IdValue:
                    current_node[part] = []
                # If the path is to a new object, start a new object, and change into it.
                else:
                    current_node[part] = {}

                current_node = current_node[part]
                continue

            # If this is a full path, copy the data, omitting null'ed fields.
            if processed[key] is not None:
                current_node[part] = processed[key]

    return unflattened
