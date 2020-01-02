Changelog
=========

0.6.4 (2020-01-02)
------------------

Fixed
~~~~~

-  Restore prior order of ``ocid`` key in merged releases.

0.6.3 (2020-01-02)
------------------

Changed
~~~~~~~

-  Improve performance of ``flatten``.

Added
~~~~~

-  Extract ``flat_append`` from ``append`` in ``MergedRelease``, to enable custom flattening methods.

0.6.2 (2019-12-31)
------------------

Changed
~~~~~~~

-  Rename ``errors`` module to ``exceptions``.

0.6.1 (2019-12-30)
------------------

Changed
~~~~~~~

-  Improve performance.

0.6.0 (2019-12-29)
------------------

Changed
~~~~~~~

-  Replace ``merge`` and ``merged_versioned`` functions with ``Merger`` class.

Fixed
~~~~~

-  ``rule_overrides`` keys omit array indexes.

0.5.12 (2019-12-19)
-------------------

Fixed
~~~~~

-  ``MissingDateKeyError`` is now initialized correctly.

0.5.11 (2019-11-28)
-------------------

Changed
~~~~~~~

-  ``MissingDateKeyError`` inherits from ``KeyError``, and ``NonObjectReleaseError``, ``NullDateValueError`` and ``NonStringDateValueError`` inherit from ``TypeError``, to allow exception handling of versions less than 0.5.2 to remain unchanged.

0.5.10.post3 (2019-11-28)
-------------------------

Changed
~~~~~~~

-  The collision behavior is changed to always warn.
-  Remove the ``collision_behavior`` argument. Use a `warning filter <https://docs.python.org/3.8/library/warnings.html>`__ instead.
-  Add ``path`` and ``id`` properties to ``DuplicateIdValueWarning`` to store the ``path`` at which, and the ``id`` on which, the collision occurred.

0.5.10.post2 (2019-11-22)
-------------------------

Changed
~~~~~~~

-  Add a ``rule_overrides`` argument to ``merge``, ``merge_versioned``, ``add_release_to_compiled_release`` and ``add_release_to_versioned_release``, which can be set on a per-field basis to:

   -  ``ocdsmerge.MERGE_BY_POSITION``: merge objects in the array based on their array index, instead of their ``id`` value.
   -  ``ocdsmerge.APPEND``: retain all objects in the array.

-  Remove these flags as possible values of ``collision_behavior``.

0.5.10.post1 (2019-11-21)
-------------------------

Changed
~~~~~~~

-  The collision behavior is changed to silently ignore the collision, by default.
-  Add these flags as possible values of ``collision_behavior``:

   -  ``ocdsmerge.MERGE_BY_POSITION``: merge objects in arrays based on their array index, instead of their ``id`` value.
   -  ``ocdsmerge.APPEND``: retain all objects in arrays.

-  Remove the ``ocdsmerge.IGNORE`` flag.

0.5.10 (2019-11-21)
-------------------

Changed
~~~~~~~

-  Warn if multiple objects in an array have the same ``id`` value.
-  Add a ``collision_behavior`` argument to ``merge``, ``merge_versioned``, ``add_release_to_compiled_release`` and ``add_release_to_versioned_release``, which can be set to:

   -  ``ocdsmerge.WARN``: issue a ``DuplicateIdValueWarning`` `warning <https://docs.python.org/3.8/library/warnings.html>`__ (default)
   -  ``ocdsmerge.RAISE``: raise a ``DuplicateIdValueError`` exception
   -  ``ocdsmerge.IGNORE``: silently ignore the collision

0.5.9 (2019-11-20)
------------------

Fixed
~~~~~

-  ``get_tags`` no longer returns duplicate tags.

0.5.8 (2019-10-21)
------------------

Changed
~~~~~~~

-  Added exception messages to all exceptions.

Fixed
~~~~~

-  If there is more than one release, but a ``date`` field is neither a string nor null, the ``NonStringDateValueError`` exception is raised, instead of ``NullDateValueError``.
-  If a release is not an object, the ``NonObjectReleaseError`` exception is raised, instead of ``NullDateValueError``.
-  If there is a ``TypeError`` for any other reason, it is raised as-is, instead of ``NullDateValueError``.

0.5.7 (2019-08-09)
------------------

-  Fix package: Rename VCR cassettes for Windows users.

0.5.6 (2019-07-30)
------------------

-  Fix package: Remove ``tests`` from build.

0.5.5 (2019-07-29)
------------------

-  Fix package: Add VCR cassettes to ``MANIFEST.in``.

0.5.4 (2019-07-29)
------------------

-  Fix package: Add ``MANIFEST.in`` and allow tests to run offline.

0.5.3 (2019-06-26)
------------------

Changed
~~~~~~~

-  Use ``https://`` instead of ``http://`` for ``standard.open-contracting.org``.

Added
~~~~~

-  Extract the inner loops of ``merge`` and ``merge_versioned`` to ``add_release_to_compiled_release`` and ``add_release_to_versioned_release``, respectively.

0.5.2 (2019-05-24)
------------------

Changed
~~~~~~~

-  If there is more than one release, but a ``date`` field is either missing or null, the ``MissingDateKeyError`` and ``NullDateValueError`` exceptions are raised, respectively, instead of the generic ``KeyError`` and ``TypeError``.

Fixed
~~~~~

-  If a field’s value is set to ``null``, it is omitted from the compiled release.
-  If a field’s value is an empty object or empty array in a release, skip it.

0.5.1 (2019-01-09)
------------------

Changed
~~~~~~~

-  ``get_tags`` and ``get_release_schema_url`` replace ``get_latest_version`` and ``get_latest_release_schema_url``.

0.5 (2019-01-04)
----------------

Advisories
~~~~~~~~~~

-  Behavior is undefined and inconsistent if an array is not defined in the schema and contains only objects in some releases but not in others. `0a81a43 <https://github.com/open-contracting/ocds-merge/commit/0a81a432b09c720ff9d81599a539072325b4fb27>`__
-  For developers using this library as a reference implementation: ``versionId`` is ignored by this library, as it merely *assists* in identifying which ``id`` fields are not on objects in arrays.

The following behaviors were previously undocumented, though they are implied by the merge rules:

-  If an array doesn’t set ``wholeListMerge`` and its objects have the same ``id`` in the same release, only the last object is retained. `66d2352 <https://github.com/open-contracting/ocds-merge/commit/66d2352791457f5f7436ba7049587dec4ebfaa89>`__
-  If a field sets ``omitWhenMerged``, ``wholeListMerge`` is ignored on its sub-fields.
-  If an array sets ``wholeListMerge``, ``omitWhenMerged`` is ignored on its sub-fields. `a88b618 <https://github.com/open-contracting/ocds-merge/commit/a88b6183d4da6a680d74d8078b969e30126c9ca8>`__

Added
~~~~~

-  Test cases for other implementations. See README.
-  You can specify the merge rules with a new ``merge_rules`` argument. `#17 <https://github.com/open-contracting/ocds-merge/pull/17>`__ `#18 <https://github.com/open-contracting/ocds-merge/pull/18>`__
-  You can specify a custom schema by passing parsed JSON to the existing ``schema`` argument. `4244b3f <https://github.com/open-contracting/ocds-merge/commit/4244b3f007ef8400617dcd02f9bf9659b06c3248>`__
-  If the schema isn’t provided or is a URL or file path, it is parsed once and cached. `5d2f831 <https://github.com/open-contracting/ocds-merge/commit/5d2f83183d43919156962ac909e3a5b231da7c0c>`__
-  Recognizes OCDS 1.0 ``ocdsOmit`` and ``ocdsVersion`` merge strategies. `e67353d <https://github.com/open-contracting/ocds-merge/commit/e67353d07e4a4f80c4c4f2edb9c782977b68ab7f>`__

Changed
~~~~~~~

-  Sets the ``id`` of the compiled release to a concatenation of the ``ocid`` and the latest release’s ``date``, instead of to the latest release’s ``id``. `8c89e43 <https://github.com/open-contracting/ocds-merge/commit/8c89e43871d24881316aee22ce5b13f7dbb4ccd9>`__
-  Maintains the same order as the input data, as much as possible. `#9 <https://github.com/open-contracting/ocds-merge/pull/9>`__ `da648b0 <https://github.com/open-contracting/ocds-merge/commit/da648b03ddffdb996b273d18776031c8eed3c4b8>`__

Fixed
~~~~~

The following conditions occur on structurally correct OCDS data:

-  If the items in an array were non-objects, the array wouldn’t be treated as a single value. `#14 <https://github.com/open-contracting/ocds-merge/pull/14>`__
-  If an array were mixing objects with and without ``id`` fields, the compiled release would merge objects if an array index matched an ``id`` value. The new behavior is to keep any objects without ``id`` values. `0e26402 <https://github.com/open-contracting/ocds-merge/commit/0e26402198b4df97d5d740eb92d38b6f149aece4>`__
-  If objects in an array weren’t defined in the schema and had no ``id`` fields, the objects would be merged based on array index. The new behavior is to keep all objects. `0e26402 <https://github.com/open-contracting/ocds-merge/commit/0e26402198b4df97d5d740eb92d38b6f149aece4>`__

The following conditions don’t occur in OCDS schema, but can occur in extensions:

-  If objects in an array were defined in the schema and had no ``id`` fields, and ``wholeListMerge`` were not set, the objects would be merged based on array index, instead of using the whole-list-merge strategy. `73dd088 <https://github.com/open-contracting/ocds-merge/commit/73dd088da9fbfc9035ea94f65ff8244162dc049f>`__
-  If an array were defined in the schema as having objects and non-objects, the identifier-merge strategy would sometimes be used instead of the whole-list-merge strategy. `d222e09 <https://github.com/open-contracting/ocds-merge/commit/d222e09e63cdf361c9cf072bbe8ca9b89a466e87>`__

The following conditions don’t occur in OCDS schema, or in extensions authored by the Open Contracting Partnership, but can occur in extensions authored by others:

-  If ``omitWhenMerged`` or ``wholeListMerge`` were ``false``, they were treated as ``true``, instead of being ignored. `d115fa2 <https://github.com/open-contracting/ocds-merge/commit/d115fa2802a8fc341f7265a478dd3c85ec31db63>`__
-  If ``omitWhenMerged`` were set on an array of non-objects, the array wouldn’t be omitted, instead of being omitted. `2d39a0f <https://github.com/open-contracting/ocds-merge/commit/2d39a0fe666258761d44aea81861ef42ac01a181>`__
-  If ``wholeListMerge`` were set on an object, only the latest version of the object would be retained in the compiled release, instead of merging all versions of the object. `b2a0dc6 <https://github.com/open-contracting/ocds-merge/commit/b2a0dc657bb4556c265d796c1afcc160b632cc2a>`__

0.4 (2018-01-04)
----------------

-  Use the schema to determine the merge rules.
-  Allow specifying a custom local or remote schema.

0.3 (2015-12-04)
----------------

-  Use relative imports.

0.2 (2015-12-01)
----------------

-  Move repository to open-contracting organization.

0.1 (2015-11-29)
----------------

First release.
