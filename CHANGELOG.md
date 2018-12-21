# Changelog

## 0.5

### Advisories

* Behavior is undefined and inconsistent if an array is not defined in the schema and contains objects in some releases but not in others. [0a81a43](https://github.com/open-contracting/ocds-merge/commit/0a81a432b09c720ff9d81599a539072325b4fb27)
* If a field sets `omitWhenMerged`, `wholeListMerge` is ignored on its sub-properties.
* If an array sets `wholeListMerge`, `omitWhenMerged` is ignored on its sub-properties. [a88b618](https://github.com/open-contracting/ocds-merge/commit/a88b6183d4da6a680d74d8078b969e30126c9ca8)
* If an array doesn't set `wholeListMerge` and objects have the same `id` in one release, only the last object is retained. [66d2352](https://github.com/open-contracting/ocds-merge/commit/66d2352791457f5f7436ba7049587dec4ebfaa89)
* `versionId` is ignored, as it merely assists in identifying which `id` fields are not on objects in arrays.

### Added

* Allow specifying cached or customized merge rules, with a new `merge_rules` argument to `merge` or `merge_versioned`. [#17](https://github.com/open-contracting/ocds-merge/pull/17) [#18](https://github.com/open-contracting/ocds-merge/pull/18)
* Allow specifying a custom schema as parsed JSON, with the existing `schema` argument. [4244b3f](https://github.com/open-contracting/ocds-merge/commit/4244b3f007ef8400617dcd02f9bf9659b06c3248)

### Changed

* Set the `id` of the compiled release to a concatenation of the `ocid` and the latest release's `date`, instead of to the latest release's `id`. [8c89e43](https://github.com/open-contracting/ocds-merge/commit/8c89e43871d24881316aee22ce5b13f7dbb4ccd9)
* If the schema isn't provided or is a URL or file path, parse it once and cache it. [5d2f831](https://github.com/open-contracting/ocds-merge/commit/5d2f83183d43919156962ac909e3a5b231da7c0c)
* Maintain the same order as the input data, as much as possible. [#9](https://github.com/open-contracting/ocds-merge/pull/9) [da648b0](https://github.com/open-contracting/ocds-merge/commit/da648b03ddffdb996b273d18776031c8eed3c4b8)

### Fixed

* If the items in an array were non-objects, the array would not be treated as a single value. [#14](https://github.com/open-contracting/ocds-merge/pull/14)
* If the objects in an array had no `id` fields according to the schema, the identifier merge strategy would be used instead of the whole list merge strategy. [73dd088](https://github.com/open-contracting/ocds-merge/commit/73dd088da9fbfc9035ea94f65ff8244162dc049f)
* If the objects in an array had no `id` fields, and were not in the schema, the objects would be merged based on array index.
* If an array were mixing objects and non-objects, the identifier merge strategy would sometimes be used instead of the whole list merge strategy. [d222e09](https://github.com/open-contracting/ocds-merge/commit/d222e09e63cdf361c9cf072bbe8ca9b89a466e87)
* If an array were mixing objects with and without `id` fields, the compiled release would merge objects if an array index matched an `id` value.
* If `omitWhenMerged` or `wholeListMerge` were `false`, they were treated as `true`. [d115fa2](https://github.com/open-contracting/ocds-merge/commit/d115fa2802a8fc341f7265a478dd3c85ec31db63)
* If `omitWhenMerged` were set on an array of non-objects, the array wouldn't be omitted. [2d39a0f](https://github.com/open-contracting/ocds-merge/commit/2d39a0fe666258761d44aea81861ef42ac01a181)
* If `wholeListMerge` were set on an object, only the latest version of the object would be retained in the compiled release. [b2a0dc6](https://github.com/open-contracting/ocds-merge/commit/b2a0dc657bb4556c265d796c1afcc160b632cc2a)

## 0.4 (2018-01-04)

* Use the schema to determine the merge rules.
* Allow specifying a custom local or remote schema.

## 0.3 (2015-12-04)

* Use relative imports.

## 0.2 (2015-12-01)

* Move repository to open-contracting organization.

## 0.1 (2015-11-29)

First release.
