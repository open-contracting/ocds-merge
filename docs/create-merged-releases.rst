Create Merged Releases
======================

The code samples below assume you're using OCDS 1.1.4; if you're using another version, replace :code:`'1__1__4'`.

.. _patch-schema:

1. Patch the schema
-------------------

(If you aren't using any `extensions <https://standard.open-contracting.org/latest/en/extensions/>`__, then you can skip this step.)

The `merge routine <https://standard.open-contracting.org/latest/en/schema/merging/>`__ is guided by the `release schema <https://standard.open-contracting.org/latest/en/schema/release/>`__ and any extensions to it.

Patch the schema with extensions, using `ProfileBuilder <https://ocdsextensionregistry.readthedocs.io/en/latest/api/profile_builder.html#profile-builder>`__ from the `OCDS Extension Registry <https://ocdsextensionregistry.readthedocs.io/>`__ library.

If you already know every extension used in a dataset (these might be listed in a `publication policy <https://standard.open-contracting.org/latest/en/implementation/publication_policy/>`__), patch the schema like so:

.. code:: python

   from ocdsextensionregistry import ProfileBuilder

   extensions = [
       'https://raw.githubusercontent.com/open-contracting-extensions/ocds_coveredBy_extension/master/extension.json',
       'https://raw.githubusercontent.com/open-contracting-extensions/ocds_legalBasis_extension/master/extension.json',
   ]

   builder = ProfileBuilder('1__1__4', extensions)
   patched_schema = builder.patched_release_schema()

If you have a record package, and want to add merged releases to each record, patch the schema using the extensions list in the package metadata:

.. code:: python

   import json

   from ocdsextensionregistry import ProfileBuilder

   with open('package.json') as f:
       package = json.load(f)

   extensions = package.get('extensions', [])

   builder = ProfileBuilder('1__1__4', extensions)
   patched_schema = builder.patched_release_schema()

If you have a release package, and if it contains *every* release of *every* OCID of which it contains at least one release (for example, if you have one release package for each OCID), patch the schema using the extensions list in the package metadata, as above.

Otherwise, you will need to collect all extensions across all release packages, and then patch the schema.

.. _initialize-merger:

2. Initialize the merger
------------------------

First, import this library, if you haven't already:

.. code:: python

   import ocdsmerge

Then, initialize a :class:`Merger<ocdsmerge.merge.Merger>` instance. You will use this instance repeatedly to create merged releases.

If you patched the schema, run:

.. code:: python

   merger = ocdsmerge.Merger(patched_schema)

To use any unpatched version of OCDS, like 1.0.3, run:

.. code:: python

   from ocdsmerge.util import get_release_schema_url

   merger = ocdsmerge.Merger(get_release_schema_url('1__0__3'))

To use a locally stored release schema (for example, to avoid remote requests), run:

.. code:: python

   from ocdsmerge.util import get_release_schema_url

   # Using a relative file path…
   merger = ocdsmerge.Merger(schema='release-schema.json')

   # Using an absolute file path…
   merger = ocdsmerge.Merger(schema='/absolute/path/to/release-schema.json')

Otherwise, to default to the release schema from the latest version of OCDS, run:

.. code:: python

   import ocdsmerge

   merger = ocdsmerge.Merger()

This library will then determine the merge rules from the provided schema.

If you later initialize another :class:`Merger<ocdsmerge.merge.Merger>` instance with the same URL or file path, this library will have cached the merge rules from the first initialization, to avoid unnecessary processing.

3. Collect the releases
-----------------------

This library assumes that the provided releases all have the same OCID, and that no releases are missing.

If you have a record package, and want to add merged releases to each record, each record's ``releases`` array already contains the releases to merge. Otherwise, you will need to collect all releases with a given OCID.

4. Merge the releases
---------------------

Finally, create merged releases:

.. code:: python

   # In a real-world example, the OCDS releases might be loaded from local files or remote APIs.
   releases = [
       {
           "ocid": "ocds-213czf-A",
           "id": "1",
           "date": "2014-01-01",
           "tag": ["tender"],
           "initiationType": "tender",
           "tender": {
               "id": "A",
               "procurementMethod": "selective"
           }
       },
       {
           "ocid": "ocds-213czf-A",
           "id": "2",
           "date": "2014-01-02",
           "tag": ["tender"],
           "initiationType": "tender",
           "tender": {
               "id": "A",
               "procurementMethod": "open"
           }
       }
   ]

   compiled_release = merger.create_compiled_release(releases)

   versioned_release = merger.create_versioned_release(releases)

You can then create an OCDS record using :code:`compiled_release` and :code:`versioned_release`.

.. _save-rules:

5. Save the merge rules
-----------------------

If you intend to incrementally update the record whenever there are new releases, rather than re-creating the record from scratch, store the merge rules for later use. For example, to store the merge rules in a file:

.. code:: python

   import pickle

   with open('merge-rules.pickle', 'wb') as f:
       pickle.dump(merger.merge_rules, f)
