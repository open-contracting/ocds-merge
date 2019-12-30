import uuid
import warnings
from enum import Enum, auto, unique

from ocdsmerge.errors import DuplicateIdValueWarning


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
    return {'releaseID', 'releaseDate', 'releaseTag', 'value'} == set(value)


def _path_without_array_indexes(path):
    return tuple(part for part in path if not isinstance(part, int))


def flatten(obj, merge_rules, path=None, flattened=None):
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
    if path is None:
        path = ()
    if flattened is None:
        flattened = {}

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
        new_path_merge_rules = merge_rules.get(_path_without_array_indexes(new_path), [])

        if 'omitWhenMerged' in new_path_merge_rules:
            continue
        # If it's neither an object nor an array, if it's `wholeListMerge`, if it's an array containing non-objects
        # (even if `wholeListMerge` is `false`), or if it's versioned values, use the whole list merge strategy.
        # Note: Behavior is undefined and inconsistent if the array is not in the schema and contains objects in some
        # cases but not in others.
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#whole-list-merge
        # See https://standard.open-contracting.org/1.1-dev/en/schema/merging/#objects
        elif not isinstance(value, (dict, list)) or 'wholeListMerge' in new_path_merge_rules or \
                isinstance(value, list) and any(not isinstance(item, dict) for item in value) or \
                len(value) and all(is_versioned_value(item) for item in value):
            flattened[new_path] = value
        # Recurse into non-empty objects, and arrays of objects that aren't `wholeListMerge`.
        elif value:
            flatten(value, merge_rules, new_path, flattened)

    return flattened


def process_flattened(flattened, rule_overrides):
    """
    Replace numbers in JSON paths (representing positions in arrays) with special objects. This ensures that objects
    in arrays with different `id` values have different JSON paths – and makes it easy to identify such arrays.
    """
    # Keep arrays in order.
    processed = {}

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

                    # Keep the integer index and default `part` for the warning.
                    index = part
                    default = IdValue(identifier)

                    rule_path = _path_without_array_indexes(scope)
                    rule = rule_overrides.get(rule_path)
                    if rule == MergeStrategy.APPEND:
                        part = IdValue(uuid.uuid4())
                    elif rule == MergeStrategy.MERGE_BY_POSITION:
                        part = IdValue(index)
                    else:
                        part = default

                    # Save the original value. (If the value is an integer, this avoids coercing it to a string.)
                    part.original_value = id_value

                    # Check whether the value is repeated in other objects in the array.
                    if scope not in identifiers:
                        identifiers[scope] = {}
                    if default not in identifiers[scope]:
                        identifiers[scope][default] = index
                    elif identifiers[scope][default] != index:
                        warnings.warn(DuplicateIdValueWarning(rule_path, default, 'Multiple objects have the `id` '
                                      'value {!r} in the `{}` array'.format(default, '.'.join(map(str, rule_path)))))

                    identifiers[path] = part
            new_key.append(part)
        processed[tuple(new_key)] = flattened[key]

    return processed


def unflatten(processed):
    """
    Unflattens a processed object into a JSON object.
    """
    unflattened = {}

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
                new_node = {}

            current_node[part] = new_node
            current_node = new_node

    return unflattened
