Open Contracting Data Standard Release Merge Library
====================================================

This library provides functions to merge a list of OCDS Releases into
either a compiledRelease or a versionedRelease needed to create an OCDS
Record.

Installation
------------

.. code:: shell

   pip install ocdsmerge

or clone the repository and paste:

.. code:: shell

   python setup.py install

or for development use:

.. code:: shell

   python setup.py develop

This requires setuptools to be installed. It has no dependencies outside
the stadard library so no pip requirements files are needed.

To test run:

.. code:: shell

   python -m unittest discover

Usage
-----

The only two functions are merge and merge_versioned. They both take a
list of python dicts representing OCDS releases (what you get if you
json.loads a release json).

Here is a simple example.

.. code:: python

   import ocdsmerge

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

   # what goes in an OCDS record under the compiledRelease key
   compiledRelease = ocdsmerge.merge(releases)
   # what goes in an OCDS record under the versionedRelease key
   versionedRelease = ocdsmerge.merge_versioned(releases)

This library takes no responsibly in serializing or unserializing the
json nor does it help in constructing the rest of the OCDS record.

Using different versions of release schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Note: This library only works against version 1.1 of OCDS and above*

By default the library will use the latest stable version of OCDS
release schema by fetching it online. However you may want use a
different schema version, an extended schema or just want the library to
work locally. In order to do this there is a second optional argument to
``merge`` and ``merge_versioned`` which is a string of the schema
location. If the string starts with http it will fetch the file from web
otherwise it assumes a relative (to your current working directory)
path. Full absolute paths can be used too:

.. code:: python

   # Fetch from the web
   ocdsmerge.merge(eleases, 'http://standard.open-contracting.org/schema/1__1__1/release-schema.json')

   # Use relese-schema.json in current working directory
   ocdsmerge.merge(releases, 'release-schema.json')

   # Use relese-schema.json using absolute path
   ocdsmerge.merge(releases, '/some/full/path/release-schema.json')

Using pre-processed release schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   # Extract the merging rules from the schema
   merge_rules = ocdsmerge.get_merge_rules('release-schema.json')
   # Use the merging rules
   ocdsmerge.merge(releases, merge_rules=merge_rules)
