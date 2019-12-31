Handle Bad Data
===============

The merge routine merges multiple individual releases into either a compiled release or a versioned release. Across the individual releases, it merges objects in arrays based on their ``id`` values, as described in the `OCDS documentation <https://standard.open-contracting.org/latest/en/schema/merging/>`__. This allows a publisher to, for example, disclose an upcoming milestone in one release, and set the date on which it was met in another release.

However, if objects that correspond to different things re-use ``id`` values, then only the last object is retained in the merged release, by default. (To be clear, such data has structural errors.) For example, if a publisher creates a release for each award notice in a procurement procedure, and restarts the numbering of award objects in each release from '1', then the later releases will overwrite the award objects of the earlier releases.

Similarly, if, in a single release, objects in the same array share an ``id`` value, then only the last object is retained. If so, this package issues a :code:`DuplicateIdValueWarning` warning. You can turn the warning into an exception or ignore the warning using a `warning filter <https://docs.python.org/3.8/library/warnings.html>`__. For example:

.. code:: python

   import warnings

   import ocdsmerge
   from ocdsmerge.exceptions import DuplicateIdValueWarning

   merger = ocdsmerge.Merger()

   releases = [{"awards": [{"id": "1"}, {"id": "1"}]}]

   # Raise an error, instead.
   with warnings.catch_warnings():
       warnings.filterwarnings('error', category=DuplicateIdValueWarning)
       compiled_release = merger.create_compiled_release(releases)

   # Ignore the warning, instead.
   with warnings.catch_warnings():
       warnings.filterwarnings('ignore', category=DuplicateIdValueWarning)
       compiled_release = merger.create_compiled_release(releases)

  # {'tag': ['compiled'], 'id': 'None-None', 'awards': [{'id': '1'}]}

If you know in advance that the individual releases have structural errors as described above, you can change the behavior of the merge routine by setting a :code:`rule_overrides` argument on a per-field basis:

-  :code:`ocdsmerge.MERGE_BY_POSITION`: merge objects in the given array based on their array index, instead of their ``id`` value.

   - This is appropriate if the publisher always re-publishes all prior objects in a given array, and puts them in a consistent order.

-  :code:`ocdsmerge.APPEND`: retain all objects in the given array, instead of merging any.

   - This is appropriate if the publisher never updates or re-publishes a prior object in a given array.

The field paths are specified as tuples. For example:

.. code:: python

   import ocdsmerge

   merger = ocdsmerge.Merger(rule_overrides={
       ('awards',): ocdsmerge.APPEND,
       ('contracts', 'implementation', 'milestones'): ocdsmerge.MERGE_BY_POSITION,
   })

   releases = [{
       "date": "2001-02-03T00:00:00Z",
       "awards": [{"id": "1-append"}],
       "contracts": [{
           "id": "1-merge",
           "implementation": {
               "milestones": [{"id": "1-merge-by-position"}]
           }
       }]
   }, {
       "date": "2004-05-06T00:00:00Z",
       "awards": [{"id": "1-append"}],
       "contracts": [{
           "id": "1-merge",
           "implementation": {
               "milestones": [{"id": "1-merge-by-position"}, {"id": "1-merge-by-position"}]
           }
       }]
   }]

   merger.create_compiled_release(releases)

   # {'tag': ['compiled'],
   #  'id': 'None-2004-05-06T00:00:00Z',
   #  'date': '2004-05-06T00:00:00Z',
   #  'awards': [{'id': '1-append'}, {'id': '1-append'}],
   #  'contracts': [{'id': '1-merge',
   #    'implementation': {'milestones': [{'id': '1-merge-by-position'},
   #                                      {'id': '1-merge-by-position'}]}}]}
