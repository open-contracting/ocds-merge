# Test file descriptions

## 1.0

* `suppliers.json`: OCDS 1.0 uses the whole list merge strategy for suppliers, whereas OCDS 1.1 uses the identifier merge strategy.

## 1.1

* `simple.json`: Update a string field
* `string-list.json`: Update an array-of-strings field
* `lists.json`: Update an array field, using the whole list merge strategy
* `mergeid.json`: Update an array field, using the identifier merge strategy
* `unit.json`: Update the `unit` field, to prevent regression to OCDS 1.1.3 error
* `contextual.json`: Version the `id` field if not in the context of an array

Null'ing fields:

* `initial-null.json`: Merge a single release containing a `null` value
* `null.json`: Update a first release with a second release containing a `null` value

Empty arrays and objects, in a single release, first release and second release:

* `single-empty-identifiermerge-array.json`: Merge a single release containing an empty array, using the identifier merge strategy
* `update-empty-identifiermerge-array.json`: Update a first release containing an empty array with a second release containing a non-empty array, using the identifier merge strategy
* `empty-identifiermerge-array.json`: Update a first release containing a non-empty array with a second release containing an empty array, using the identifier merge strategy

* `single-empty-wholelistmerge-array.json`: Merge a single release containing an empty array, using the whole list merge strategy
* `update-empty-wholelistmerge-array.json`: Update a first release containing an empty array with a second release containing a non-empty array, using the whole list merge strategy
* `empty-wholelistmerge-array.json`: Update a first release containing a non-empty array with a second release containing an empty array, using the whole list merge strategy

* `single-empty-object.json`: Merge a single release containing an empty object
* `update-empty-object.json`: Update a first release containing an empty object with a second release containing a non-empty object
* `empty-object.json`: Update a first release containing a non-empty object with a second release containing an object

## Schema

Read the `description` JSON Schema metadata properties in `schema.json` to understand the purpose of each test file.
