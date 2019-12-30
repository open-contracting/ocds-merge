from ocdsmerge.flatten import flatten, process_flattened, unflatten
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
            self.data = process_flattened(flatten(data, self.merge_rules), self.rule_overrides)

    def asdict(self):
        """
        Returns the merged release as a dictionary.
        """
        return unflatten(self.data)

    def extend(self, releases):
        for release in sorted_releases(releases):
            self.append(release)

    def append(self, releases):
        raise NotImplementedError('subclasses must implement append()')


class CompiledRelease(MergedRelease):
    def __init__(self, data=None, **kwargs):
        super().__init__(data, **kwargs)

        self.data[('tag',)] = ['compiled']

    def append(self, release):
        """
        Merges one release into a compiled release.
        """
        release = release.copy()

        # `ocid` and `date` are required fields, but the data can be invalid.
        ocid = release.get('ocid')
        date = release.get('date')
        # Prior to OCDS 1.1.4, `tag` didn't set "omitWhenMerged": true.
        release.pop('tag', None)  # becomes ["compiled"]

        flat = flatten(release, self.merge_rules)
        processed = process_flattened(flat, self.rule_overrides)

        # Add an `id` and `date`.
        self.data[('id',)] = '{}-{}'.format(ocid, date)
        self.data[('date',)] = date

        # In OCDS 1.0, `ocid` incorrectly sets "mergeStrategy": "ocdsOmit".
        self.data[('ocid',)] = ocid

        self.data.update(processed)


class VersionedRelease(MergedRelease):
    def append(self, release):
        """
        Merges one release into a versioned release.
        """
        release = release.copy()

        # Don't version the OCID.
        ocid = release.pop('ocid', None)
        self.data[('ocid',)] = ocid

        # `id` and `date` are required fields, but the data can be invalid.
        releaseID = release.get('id')
        date = release.get('date')
        # Prior to OCDS 1.1.4, `tag` didn't set "omitWhenMerged": true.
        tag = release.pop('tag', None)

        flat = flatten(release, self.merge_rules)
        processed = process_flattened(flat, self.rule_overrides)

        for key, value in processed.items():
            # If key is not versioned, continue. If the value is unchanged, don't add it to the history.
            if key in self.data and (not isinstance(self.data[key], list) or value == self.data[key][-1]['value']):
                continue

            if key not in self.data:
                self.data[key] = []

            self.data[key].append({
                'releaseID': releaseID,
                'releaseDate': date,
                'releaseTag': tag,
                'value': value,
            })
