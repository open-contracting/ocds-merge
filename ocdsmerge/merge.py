from ocdsmerge.flatten import flatten, unflatten
from ocdsmerge.rules import get_merge_rules
from ocdsmerge.util import sorted_releases


class Merger:
    def __init__(self, schema=None, merge_rules=None, rule_overrides=None):
        """
        Initializes a reusable ``Merger`` instance for creating merged releases.

        :param schema: the release schema (if not provided, will default to the latest version of OCDS)
        :param dict merge_rules: the merge rules (if not provided, will determine the rules from the ``schema``)
        :param dict rule_overrides: any rule overrides, in which keys are field paths as tuples, and values are either
            ``ocdsmerge.APPEND`` or ``ocdsmerge.MERGE_BY_POSITION``
        :type schema: dict or str
        """
        if merge_rules is None:
            merge_rules = get_merge_rules(schema)
        if rule_overrides is None:
            rule_overrides = {}

        self.merge_rules = merge_rules
        self.rule_overrides = rule_overrides

    def create_compiled_release(self, releases):
        """
        Merges a list of releases into a compiled release.
        """
        return self._create_merged_release(CompiledRelease, releases)

    def create_versioned_release(self, releases):
        """
        Merges a list of releases into a versioned release.
        """
        return self._create_merged_release(VersionedRelease, releases)

    def _create_merged_release(self, cls, releases):
        merged_release = cls(merge_rules=self.merge_rules, rule_overrides=self.rule_overrides)
        merged_release.extend(releases)
        return merged_release.asdict()


class MergedRelease:
    """
    Whether the class is for merging versioned releases.
    """
    versioned = None

    def __init__(self, data=None, schema=None, merge_rules=None, rule_overrides=None):
        """
        Initializes a merged release.

        :param dict data: the latest copy of the merged release, if any
        :param schema: the release schema (if not provided, will default to the latest version of OCDS)
        :param dict merge_rules: the merge rules (if not provided, will determine the rules from the ``schema``)
        :param dict rule_overrides: any rule overrides, in which keys are field paths as tuples, and values are either
            ``ocdsmerge.APPEND`` or ``ocdsmerge.MERGE_BY_POSITION``
        :type schema: dict or str
        """
        if merge_rules is None:
            merge_rules = get_merge_rules(schema)
        if rule_overrides is None:
            rule_overrides = {}

        self.merge_rules = merge_rules
        self.rule_overrides = rule_overrides

        if data is None:
            self.data = {}
        else:
            self.data = flatten(data, self.merge_rules, self.rule_overrides, flattened={}, versioned=self.versioned)

    def asdict(self):
        """
        Returns the merged release as a dictionary.
        """
        return unflatten(self.data)

    def extend(self, releases):
        """
        Sorts and merges many releases into the merged release.
        """
        for release in sorted_releases(releases):
            self.append(release)

    def append(self, release):
        """
        Merges one release into the merged release.
        """
        release = release.copy()

        # Store the values of fields that set "omitWhenMerged": true.
        ocid = release.get('ocid')
        release_id = release.get('id')
        date = release.get('date')
        # Prior to OCDS 1.1.4, `tag` didn't set "omitWhenMerged": true.
        tag = release.pop('tag', None)

        flat = flatten(release, self.merge_rules, self.rule_overrides, flattened={})
        self.flat_append(flat, ocid, release_id, date, tag)

    def flat_append(self, flat, ocid, release_id, date, tag):
        raise NotImplementedError('subclasses must implement flat_append()')


class CompiledRelease(MergedRelease):
    versioned = False

    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)
        self.data[('tag',)] = ['compiled']

    def flat_append(self, flat, ocid, release_id, date, tag):
        # Add an `id` and `date`.
        self.data[('id',)] = '{}-{}'.format(ocid, date)
        self.data[('date',)] = date
        # In OCDS 1.0, `ocid` incorrectly sets "mergeStrategy": "ocdsOmit".
        self.data[('ocid',)] = ocid

        self.data.update(flat)


class VersionedRelease(MergedRelease):
    versioned = True

    def flat_append(self, flat, ocid, release_id, date, tag):
        # Don't version the OCID.
        flat.pop(('ocid',), None)
        self.data[('ocid',)] = ocid

        for key, value in flat.items():
            # If key is not versioned, continue. If the value is unchanged, don't add it to the history.
            if key in self.data and (type(self.data[key]) is not list or value == self.data[key][-1]['value']):
                continue

            self.data.setdefault(key, []).append({
                'releaseID': release_id,
                'releaseDate': date,
                'releaseTag': tag,
                'value': value,
            })
