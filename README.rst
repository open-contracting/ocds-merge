|PyPI Version| |Build Status| |Coverage Status| |Python Version|

This Python package creates records that conform to the `Open Contracting Data Standard <https://standard.open-contracting.org>`__. Specifically, it provides classes for merging OCDS releases with the same OCID into either a compiled release or a versioned release (collectively called "merged releases"), as described in the `OCDS documentation <https://standard.open-contracting.org/latest/en/schema/merging/>`__.

Instead of using this library directly, it is easier to create merged releases using either:

-  `OCDS Kit <https://ocdskit.readthedocs.io/>`__'s `compile <https://ocdskit.readthedocs.io/en/latest/cli/ocds.html#compile>`__ command-line tool
-  OCDS Kit's `merge <https://ocdskit.readthedocs.io/en/latest/api/combine.html#ocdskit.combine.merge>`__ Python function
-  `OCDS Toucan <https://toucan.open-contracting.org/>`__'s `compile releases <https://toucan.open-contracting.org/compile/>`__ web application

If you are viewing this on GitHub or PyPi, open the `full documentation <https://ocds-merge.readthedocs.io/>`__ for additional details.

.. |PyPI Version| image:: https://img.shields.io/pypi/v/ocdsmerge.svg
   :target: https://pypi.org/project/ocdsmerge/
.. |Build Status| image:: https://secure.travis-ci.org/open-contracting/ocds-merge.png
   :target: https://travis-ci.org/open-contracting/ocds-merge
.. |Coverage Status| image:: https://coveralls.io/repos/github/open-contracting/ocds-merge/badge.svg?branch=master
   :target: https://coveralls.io/github/open-contracting/ocds-merge?branch=master
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ocdsmerge.svg
   :target: https://pypi.org/project/ocdsmerge/
