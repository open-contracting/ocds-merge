import collections

NOT_FLATTEN_KEYS = ['additionalIdentifiers', 
                    'additionalClassifications',
                    'suppliers',
                    'changes',
                    'tenderers'
                   ]

class IdValue(str):
    '''This is basically a string but is used to differentiate itself when doing an ininstance check.'''
    def __init__(self, value):
         ## Save original value. this is needed if id was originally an integer and you want to keep that iformation.
         self.original_value = value
         str.__init__(value)


def flatten(path, flattened, obj):
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
        # We do not flatten these keys as the child lists of 
        # these keys will not be merged, be totally replaced
        # and versioned as a whole
        if isinstance(value, (dict, list)) and key not in NOT_FLATTEN_KEYS:
            flatten(path + (key,), flattened, value)
        else:
            flattened[path + (key,)] = value
    return flattened

def unflatten(flattened):
    '''Unflatten flattened object back into nested form.'''
    unflattened = {}
    for flat_key in flattened:
        current_pos = unflattened
        for num, item in enumerate(flat_key):
            if isinstance(item, IdValue):
                if len(flat_key) - 1 == num: #when this is an array of string or ints
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
    for key in sorted(flattened.keys(), key=lambda a: (len(a),) + a):
        new_key = []
        for num, item in enumerate(key):
            if isinstance(item, int):
                id_value = flattened.get(tuple(key[:num+1]) + ('id',))
                if id_value is None:
                    id_value = item
                new_key.append(IdValue(id_value))
                continue
            new_key.append(item)
        processed[tuple(new_key)] = flattened[key]
    return processed


def merge(releases):
    ''' Takes a list of releases and merge them making a 
    compiledRelease suitible for an OCDS Record '''
    merged = collections.OrderedDict({("tag",): ['compiled']})
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        release.pop('tag', None)

        flat = flatten((), {}, release)

        processed = process_flattened(flat)
        # In flattening and adding the ids to the json path
        # we make sure each json path is going to same as long as
        # all the ids match. Position in the array is not relevent 
        # (however it will keep this order anyway due to having an ordered dict). 
        # This makes the actual merging come down to
        # just this statement.
        merged.update(processed)
    return unflatten(merged)

def merge_versioned(releases):
    ''' Takes a list of releases and merge them making a 
    versionedRelease suitible for an OCDS Record '''
    merged = collections.OrderedDict()
    for release in sorted(releases, key=lambda rel: rel["date"]):
        release = release.copy()
        ocid = release.pop("ocid")
        merged[("ocid",)] = ocid

        releaseID = release.pop("id")
        date = release.pop("date")
        tag = release.pop('tag', None)
        flat = flatten((), {}, release)

        processed = process_flattened(flat)

        for key, value in processed.items():
            if key[-1] == 'id' and isinstance(key[-2], tuple):
                merged[key] = value
                continue
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


