OCDS Merge |release|
====================

.. include:: ../README.rst

To install::

   pip install ocdsmerge

You can either :doc:`create a new merged release<create-merged-releases>` from a list of individual releases, or :doc:`update an existing merged release<update-merged-releases>` with one or more individual releases.

If the data you are working with has bad ``id`` values, use the features for :doc:`handling bad data<handle-bad-data>`.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   create-merged-releases.rst
   update-merged-releases.rst
   handle-bad-data.rst
   api/index.rst
   changelog.rst

Reference implementation
------------------------

This library serves as a reference implementation of OCDS' `merge routine <https://standard.open-contracting.org/latest/en/schema/merging/>`__. You can read the commented code on `GitHub <https://github.com/open-contracting/ocds-merge>`__.

Test cases
~~~~~~~~~~

We provide test cases for other implementations of the merge routine under the `tests/fixtures <https://github.com/open-contracting/ocds-merge/tree/master/tests/fixtures>`__ directory. The ``1.0`` and ``1.1`` directories contain files like ``simple.json``, which contain a list of OCDS releases as JSON; the suffixed ``simple-compiled.json`` and ``simple-versioned.json`` files contain the expected compiled release and versioned release, respectively. To test your implementation, provide as input a file like ``simple.json`` as well as the appropriate version of the OCDS release schema, and compare your output to files like ``simple-compiled.json`` and ``simple-versioned.json``.

To prepare your implementation for future versions and third-party extensions, you can test your implementation using the files under the ``schema`` directory and using the schema in the `schema.json <https://github.com/open-contracting/ocds-merge/blob/master/tests/fixtures/schema.json>`__ file.

In future, we can consider providing a more formal test suite, like that of `CSV on the Web <http://w3c.github.io/csvw/tests/>`__. Please contact data@open-contracting.org if interested.

Copyright (c) 2015 Open Contracting Partnership, released under the BSD license
