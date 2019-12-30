Update Merged Releases
======================

If you already have a `record <https://standard.open-contracting.org/latest/en/getting_started/releases_and_records/#records>`__, and want to update its compiled release or versioned release, you can either:

-  :doc:`create merged releases<create-merged-releases>` from scratch, using all individual releases with the same OCID
-  update an existing merged release with any new individual releases, as described below

1. Load the merge rules
-----------------------

When creating merged releases from scratch, you had to :ref:`initialize<initialize-merger>` a :class:`Merger<ocdsmerge.merge.Merger>` instance, which determined merge rules from a given schema.

You can :ref:`patch the schema<patch-schema>` and :ref:`initialize the merger<initialize-merger>` as before, or, if you :ref:`saved the merge rules<save-rules>`, you can initialize the merger with them, instead. For example:

.. code:: python

   import pickle

   with open('merge-rules.pickle', 'rb') as f:
       rules = pickle.load(f)

This guarantees that the merged release will be updated following the same rules as when it was created. However, if any extensions are added or changed, you will need to patch the schema and initialize the merger as before.

2. Initialize the merger
------------------------

To create merged releases from scratch, a :class:`Merger<ocdsmerge.merge.Merger>` instance was used. To update merged releases, instead, use a :class:`CompiledRelease<ocdsmerge.merge.CompiledRelease>` or :class:`VersionedRelease<ocdsmerge.merge.VersionedRelease>` instance, which accepts an existing merged release as input. For example:

.. code:: python

   import ocdsmerge

   compiled_release = {
       "tag": ["compiled"],
       "id": "ocds-213czf-A-2014-01-02T00:00:00Z",
       "date": "2014-01-02T00:00:00Z",
       "ocid": "ocds-213czf-A",
       "initiationType": "tender",
       "tender": {
           "id": "A",
           "procurementMethod": "open"
       }
   }

   merger = ocdsmerge.CompiledRelease(compiled_release, merge_rules=rules)

3. Add the individual releases
------------------------------

You can add many releases at once, in which case the merger sorts the releases by ``date``:

.. code:: python

   releases = [
      {
          "ocid": "ocds-213czf-A",
          "id": "3",
          "date": "2014-01-03",
          "tag": ["tender"],
          "initiationType": "tender",
          "tender": {
              "status": "complete"
          }
      }
   ]

   merger.extend(releases)

   compiled_release = merger.asdict()

Or, you can add one release at a time, ensuring they are ordered by ``date``:

.. code:: python

   release = {
       "ocid": "ocds-213czf-A",
       "id": "3",
       "date": "2014-01-03",
       "tag": ["tender"],
       "initiationType": "tender",
       "tender": {
           "status": "complete"
       }
   }

   merger.append(release)

   compiled_release = merger.asdict()

You can then update the OCDS record using :code:`compiled_release`.
