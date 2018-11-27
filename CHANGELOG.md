# Changelog

## 0.5

### Added

* Allow specifying cached or customized merge rules.
* Allow specifying a custom schema as parsed JSON.

### Fixed

* If `omitWhenMerged`, `versionId`, `wholeListMerge` were `false`, they were treated as `true`.
* If `omitWhenMerged` were set on an array of non-objects, the list wouldn't be omitted.
* If an array mixed objects and non-objects, the identifier merge strategy would sometimes be used instead of the whole list merge strategy.

## 0.4 (2018-01-04)

* Use the schema to determine the merge rules.
* Allow specifying a custom local or remote schema.

## 0.3 (2015-12-04)

* Use relative imports.

## 0.2 (2015-12-01)

* Move repository to open-contracting organization.

## 0.1 (2015-11-29)

First release.
