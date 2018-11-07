import collections
import requests
import jsonref


class IdValue(str):
    '''This is basically a string but is used to differentiate itself when doing an ininstance check.'''

    def __init__(self, value):
        # Save original value. this is needed if id was originally an integer and you want to keep that iformation.
        self.original_value = value
        str.__init__(value)


def get_latest_schema_uri():
    schema_list_page = requests.get('http://standard.open-contracting.org/schema').text

    parts = schema_list_page.split('href="')
    all_versions = []
    for part in parts:
        start = part[:part.find('"')].strip("/")
        version_parts = tuple(start.split("__"))
        if len(version_parts) != 3 or version_parts[-1] == "RC":
            continue
        all_versions.append(version_parts)
    all_versions.sort()
    latest_version = "__".join(all_versions[-1])

    return 'http://standard.open-contracting.org/schema/' + latest_version + '/release-schema.json'


def merge_rule_generate(properties, current_path):
    for key, value in properties.items():
        prop_type = value.get('type')
        if not prop_type:
            continue
        new_path = current_path + (key,)

        special_props = []
        for special_prop in ['omitWhenMerged', 'versionId', 'wholeListMerge']:
            if special_prop in value:
                special_props.append(special_prop)
        if special_props:
            yield (new_path, special_props)

        if 'object' in prop_type and 'properties' in value:
            yield from merge_rule_generate(value['properties'], current_path=new_path)
        if 'array' in prop_type and 'items' in value and 'object' in value['items']['type']:
            yield from merge_rule_generate(value['items']['properties'], current_path=new_path)


def remove_number_path(path):
    return tuple(item for item in path if not isinstance(item, int))


def process_schema(schema):
    schema = schema or get_latest_schema_uri()
    if schema.startswith('http'):
        deref_schema = jsonref.load_uri(schema)
    else:
        with open(schema) as f:
            deref_schema = jsonref.load(f)
    return dict(merge_rule_generate(deref_schema['properties'], tuple()))


def flatten(path, flattened, obj, merge_rules):
    '''Flatten any nested json object into simple key value pairs.
       The key is the json path represented as a tuple.
       eg. {"a": "I am a", "b": ["A", "list"], "c": [{"ca": "I am ca"}, {"cb": "I am cb"}]}
       will flatten to
       {('a',): 'I am a',
        ('b', 1): 'list',
        ('c', 0, 'ca'): 'I am ca',
        ('b', 0): 'A',
        ('c', 1, 'cb'): 'I am cb'}
    '''
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
    '''Unflatten flattened object back into nested form.'''
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
    ''' Replace numbers in json path (representing position in arrays)
        with special id object. This is to make detecting what is an
        array possible without needed to check schema.'''

    # Keep ordered so that arrays will stay in the same order.
    processed = collections.OrderedDict()
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
    ''' Takes a list of releases and merge them making a
    compiledRelease suitible for an OCDS Record '''
    if not merge_rules:
        merge_rules = process_schema(schema)
    merged = collections.OrderedDict({("tag",): ['compiled']})
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        release.pop('tag', None)

        releaseID = release.pop("id")
        date = release.pop("date")

        flat = flatten((), collections.OrderedDict(), release, merge_rules)

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
    ''' Takes a list of releases and merge them making a
    versionedRelease suitible for an OCDS Record '''
    if not merge_rules:
        merge_rules = process_schema(schema)
    merged = collections.OrderedDict()
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        ocid = release.pop("ocid")
        merged[("ocid",)] = ocid

        releaseID = release.pop("id")
        date = release.pop("date")
        tag = release.pop('tag', None)
        flat = flatten((), collections.OrderedDict(), release, merge_rules)

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
