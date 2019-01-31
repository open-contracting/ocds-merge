OCDS Merge
==========

|PyPI Version| |Build Status| |Coverage Status| |Python Version|

This Python package helps to create records that conform to the `Open Contracting Data Standard <http://standard.open-contracting.org>`__. Specifically, it provides functions for merging OCDS releases with the same OCID into either a compiled release or a versioned release.

::

   pip install ocdsmerge

Usage
-----

The two main functions are :code:`merge` and :code:`merge_versioned`. They take OCDS releases as input, and return a compiled release or a versioned release as output, respectively. For example:

.. code:: python

   import ocdsmerge

   # In a real-world example, the OCDS releases might be loaded from JSON files.
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

   compiledRelease = ocdsmerge.merge(releases)

   versionedRelease = ocdsmerge.merge_versioned(releases)

You can then create an OCDS record using the :code:`compiledRelease` and :code:`versionedRelease`.

Important caveats
~~~~~~~~~~~~~~~~~

* You must ensure that the OCDS releases that you provide as input have the same OCID.
* If you are using an older version of the OCDS release schema, you must specify the older schema as a URL, file path, or Python dictionary (see below).
* If you are using OCDS extensions, you should patch the OCDS release schema (for instance, using `json-merge-patch <https://pypi.org/project/json-merge-patch/>`__) and specify the patched schema as a URL, file path, or Python dictionary.

Using different release schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the :code:`merge` and :code:`merge_versioned` functions use the latest version of the OCDS release schema, which they download once. However, you may want to use an older version, an extended schema, or a local schema to avoid remote requests. To do so, use the optional :code:`schema` argument, which can be:

* A URL to a release schema, as a string starting with ``http``
* A file path to a release schema, as a string
* a release schema, as a Python dictionary

.. code:: python

   # URL
   ocdsmerge.merge(releases, schema='http://standard.open-contracting.org/schema/1__0__3/release-schema.json')

   # Relative file path
   ocdsmerge.merge(releases, schema='release-schema.json')

   # Absolute file path
   ocdsmerge.merge(releases, schema='/absolute/path/to/release-schema.json')

   # A Python dictionary, stored in a `release_schema` variable
   ocdsmerge.merge(releases, schema=release_schema)

Using cached merge rules
~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`merge` and :code:`merge_versioned` functions extract merge rules from the release schema. If the release schema were provided as a string (i.e. as a URL or file path), then these merge rules are automatically cached between function calls. However, if it were provided as a Python dictionary, then they won't be cached. To manually cache merge rules, use the :code:`get_merge_rules` function:

.. code:: python

   merge_rules = ocdsmerge.get_merge_rules('release-schema.json')

   ocdsmerge.merge(releases, merge_rules=merge_rules)

Reference implementation
------------------------

This package serves as a reference implementation of OCDS merging. You can read its commented code in `merge.py <https://github.com/open-contracting/ocds-merge/blob/master/ocdsmerge/merge.py>`__.

Test cases
~~~~~~~~~~

We provide test cases for other implementations of OCDS merging under the `tests/fixtures <https://github.com/open-contracting/ocds-merge/tree/master/tests/fixtures>`__ directory. The ``1.0`` and ``1.1`` directories contain files like ``simple.json``, which contain a list of OCDS releases as JSON; the suffixed ``simple-compiled.json`` and ``simple-versioned.json`` files contain the expected compiled release and versioned release respectively. To test your implementation, provide as input a file like ``simple.json`` as well as the appropriate version of the OCDS release schema, and compare your output to files like ``simple-compiled.json`` and ``simple-versioned.json``.

To prepare your implementation for future versions and third-party extensions, you can test your implementation using the files under the ``schema`` directory and using the schema in the `schema.json <https://github.com/open-contracting/ocds-merge/blob/master/tests/fixtures/schema.json>`__ file.

In future, we can consider providing a more formal test suite, like those for `CSV on the Web <http://w3c.github.io/csvw/tests/>`__. Please contact data@open-contracting.org if interested.

Copyright (c) 2015 Open Contracting Partnership, released under the BSD license

.. |PyPI Version| image:: https://img.shields.io/pypi/v/ocdsmerge.svg
   :target: https://pypi.org/project/ocdsmerge/
.. |Build Status| image:: https://secure.travis-ci.org/open-contracting/ocds-merge.png
   :target: https://travis-ci.org/open-contracting/ocds-merge
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/ocds-merge/badge.svg?branch=master
   :target: https://coveralls.io/github/open-contracting/ocds-merge?branch=master
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ocdsmerge.svg
   :target: https://pypi.org/project/ocdsmerge/
