# Changelog

## 0.5

### Advisories

* Behavior is undefined and inconsistent if an array is not defined in the schema and contains objects in some releases but not in others.
* If a field sets `omitWhenMerged`, `wholeListMerge` is ignored on its sub-properties.
* If an array sets `wholeListMerge`, `omitWhenMerged` is ignored on its sub-properties.
* If an array doesn't set `wholeListMerge` and objects have the same `id` in one release, only the last object is retained.
* `versionId` is ignored, as it merely assists in identifying which `id` fields are not on objects in arrays.

### Added

* Allow specifying cached or customized merge rules.
* Allow specifying a custom schema as parsed JSON.

### Changed

* Set the `id` of the compiled release to a concatenation of the `ocid` and the latest release's `date`, instead of to the latest release's `id`.
* Maintain the same order as the input data, as much as possible.

### Fixed

* If `omitWhenMerged` or `wholeListMerge` were `false`, they were treated as `true`.
* If `omitWhenMerged` were set on an array of non-objects, the list wouldn't be omitted.
* If `wholeListMerge` were set on an object, only the latest version of the object would be retained in the compiled release.
* If the objects in an array had no `id` field according to the schema, the identifier merge strategy would be used instead of the whole list merge strategy.
* If an array were mixing objects and non-objects, the identifier merge strategy would sometimes be used instead of the whole list merge strategy.
* If the items in an array were non-objects, the list would not be treated as a single value. [#14](https://github.com/open-contracting/ocds-merge/pull/14)

## 0.4 (2018-01-04)

* Use the schema to determine the merge rules.
* Allow specifying a custom local or remote schema.

## 0.3 (2015-12-04)

* Use relative imports.

## 0.2 (2015-12-01)

* Move repository to open-contracting organization.

## 0.1 (2015-11-29)

First release.
