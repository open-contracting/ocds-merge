# Changelog

## 0.5.4 (2019-07-29)

* Add `MANIFEST.in`.
* Fix tests to run offline.

## 0.5.3 (2019-06-26)

### Changed

* Use `https://` instead of `http://` for `standard.open-contracting.org`.

### Added

* Extract the inner loops of `merge` and `merge_versioned` to `add_release_to_compiled_release` and `add_release_to_versioned_release`, respectively.

## 0.5.2 (2019-05-24)

### Changed

* If there is more than one release, but the `date` field is missing or null, the `MissingDateKeyError` and `NullDateValueError` exceptions are raised, respestively, instead of the generic `KeyError` and `TypeError`.

### Fixed

* If a field's value is set to `null`, it is omitted from the compiled release.
* If a field's value is an empty object or empty array in a release, skip it.

## 0.5.1 (2019-01-09)

### Changed

* `get_tags` and `get_release_schema_url` replace `get_latest_version` and `get_latest_release_schema_url`.

## 0.5 (2019-01-04)

### Advisories

* Behavior is undefined and inconsistent if an array is not defined in the schema and contains only objects in some releases but not in others. [0a81a43](https://github.com/open-contracting/ocds-merge/commit/0a81a432b09c720ff9d81599a539072325b4fb27)
* For developers using this library as a reference implementation: `versionId` is ignored by this library, as it merely *assists* in identifying which `id` fields are not on objects in arrays.

The following behaviors were previously undocumented, though they are implied by the merge rules:

* If an array doesn't set `wholeListMerge` and its objects have the same `id` in the same release, only the last object is retained. [66d2352](https://github.com/open-contracting/ocds-merge/commit/66d2352791457f5f7436ba7049587dec4ebfaa89)
* If a field sets `omitWhenMerged`, `wholeListMerge` is ignored on its sub-fields.
* If an array sets `wholeListMerge`, `omitWhenMerged` is ignored on its sub-fields. [a88b618](https://github.com/open-contracting/ocds-merge/commit/a88b6183d4da6a680d74d8078b969e30126c9ca8)

### Added

* Test cases for other implementations. See README.
* You can specify the merge rules with a new `merge_rules` argument. [#17](https://github.com/open-contracting/ocds-merge/pull/17) [#18](https://github.com/open-contracting/ocds-merge/pull/18)
* You can specify a custom schema by passing parsed JSON to the existing `schema` argument. [4244b3f](https://github.com/open-contracting/ocds-merge/commit/4244b3f007ef8400617dcd02f9bf9659b06c3248)
* If the schema isn't provided or is a URL or file path, it is parsed once and cached. [5d2f831](https://github.com/open-contracting/ocds-merge/commit/5d2f83183d43919156962ac909e3a5b231da7c0c)
* Recognizes OCDS 1.0 `ocdsOmit` and `ocdsVersion` merge strategies. [e67353d](https://github.com/open-contracting/ocds-merge/commit/e67353d07e4a4f80c4c4f2edb9c782977b68ab7f)

### Changed

* Sets the `id` of the compiled release to a concatenation of the `ocid` and the latest release's `date`, instead of to the latest release's `id`. [8c89e43](https://github.com/open-contracting/ocds-merge/commit/8c89e43871d24881316aee22ce5b13f7dbb4ccd9)
* Maintains the same order as the input data, as much as possible. [#9](https://github.com/open-contracting/ocds-merge/pull/9) [da648b0](https://github.com/open-contracting/ocds-merge/commit/da648b03ddffdb996b273d18776031c8eed3c4b8)

### Fixed

The following conditions occur on structurally correct OCDS data:

* If the items in an array were non-objects, the array wouldn't be treated as a single value. [#14](https://github.com/open-contracting/ocds-merge/pull/14)
* If an array were mixing objects with and without `id` fields, the compiled release would merge objects if an array index matched an `id` value. The new behavior is to keep any objects without `id` values. [0e26402](https://github.com/open-contracting/ocds-merge/commit/0e26402198b4df97d5d740eb92d38b6f149aece4)
* If objects in an array weren't defined in the schema and had no `id` fields, the objects would be merged based on array index. The new behavior is to keep all objects. [0e26402](https://github.com/open-contracting/ocds-merge/commit/0e26402198b4df97d5d740eb92d38b6f149aece4)

The following conditions don't occur in OCDS schema, but can occur in extensions:

* If objects in an array were defined in the schema and had no `id` fields, and `wholeListMerge` were not set, the objects would be merged based on array index, instead of using the whole-list-merge strategy. [73dd088](https://github.com/open-contracting/ocds-merge/commit/73dd088da9fbfc9035ea94f65ff8244162dc049f)
* If an array were defined in the schema as having objects and non-objects, the identifier-merge strategy would sometimes be used instead of the whole-list-merge strategy. [d222e09](https://github.com/open-contracting/ocds-merge/commit/d222e09e63cdf361c9cf072bbe8ca9b89a466e87)

The following conditions don't occur in OCDS schema, or in extensions authored by the Open Contracting Partnership, but can occur in extensions authored by others:

* If `omitWhenMerged` or `wholeListMerge` were `false`, they were treated as `true`, instead of being ignored. [d115fa2](https://github.com/open-contracting/ocds-merge/commit/d115fa2802a8fc341f7265a478dd3c85ec31db63)
* If `omitWhenMerged` were set on an array of non-objects, the array wouldn't be omitted, instead of being omitted. [2d39a0f](https://github.com/open-contracting/ocds-merge/commit/2d39a0fe666258761d44aea81861ef42ac01a181)
* If `wholeListMerge` were set on an object, only the latest version of the object would be retained in the compiled release, instead of merging all versions of the object. [b2a0dc6](https://github.com/open-contracting/ocds-merge/commit/b2a0dc657bb4556c265d796c1afcc160b632cc2a)

## 0.4 (2018-01-04)

* Use the schema to determine the merge rules.
* Allow specifying a custom local or remote schema.

## 0.3 (2015-12-04)

* Use relative imports.

## 0.2 (2015-12-01)

* Move repository to open-contracting organization.

## 0.1 (2015-11-29)

First release.
