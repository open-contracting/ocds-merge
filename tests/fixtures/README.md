# Test file descriptions

## 1.0

* `suppliers.json`: OCDS 1.0 uses the whole list merge strategy for suppliers, whereas OCDS 1.1 uses the identifier merge strategy.

## 1.1

Updating values:

* `simple.json`: Update a string field
* `string-list.json`: Update an array-of-strings field
* `lists.json`: Update an array field, using the whole list merge strategy
* `mergeid.json`: Update an array field, using the identifier merge strategy
* `unit.json`: Update the `unit` field, to prevent regression to OCDS 1.1.3 error

Versioning values:

* `contextual.json`: Version the `id` field if not in the context of an array

Removing fields:

* `initial-null.json`: Merge a single release containing a `null` value
* `null.json`: Update a first release with a second release containing a `null` value

Empty arrays and objects, in a single release, first release or second release:

* Array using the identifier merge strategy
  * `single-empty-identifiermerge-array.json`: Merge a single release containing an empty array
  * `fill-identifiermerge-array.json`: Update a first release containing an empty array with a second release containing a non-empty array
  * `empty-identifiermerge-array.json`: Update a first release containing a non-empty array with a second release containing an empty array
* Array using the whole list merge strategy
  * `single-empty-wholelistmerge-array.json`: Merge a single release containing an empty array
  * `fill-wholelistmerge-array.json`: Update a first release containing an empty array with a second release containing a non-empty array
  * `empty-wholelistmerge-array.json`: Update a first release containing a non-empty array with a second release containing an empty array
* Object
  * `single-empty-object.json`: Merge a single release containing an empty object
  * `fill-object.json`: Update a first release containing an empty object with a second release containing a non-empty object
  * `empty-object.json`: Update a first release containing a non-empty object with a second release containing an object

## Schema

Read the `description` JSON Schema metadata properties in `schema.json` to understand the purpose of each test file.

* `identifier-merge-collision.json`: An object without an `id` field at an array index that matches the value of the `id` field of another object shouldn't be overwritten
* `identifier-merge-duplicate-id.json`: If there are many objects with the same value for the `id` field in the same release, the last object should be retained (identifier merge)
* `no-top-level-id.json`: If an object in an array has no `id` field, it should be retained (identifier merge)
* `whole-list-merge-duplicate-id.json`: If there are many objects with the same value for the `id` field in the same release, all the objects should be retained (whole list merge)
* `whole-list-merge-empty.json`: An empty array should replace a previous array (whole list merge)

Prevent regressions to 0.4 errors on edge cases:

* `merge-property-is-false.json`
* `omit-when-merged-array-of-non-objects.json`
* `whole-list-merge-object.json`
