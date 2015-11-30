Open Contracting Data Standard Release Merge Library
==============================================

This library provides functions to merge a list of OCDS Releases into either a compiledRelease or a versionedRelease needed to create an OCDS Record.

Installation
-------------
```
pip install ocdsmerge
```
or clone the repository and paste:
```
python setup.py install
```
or for development use:
```
python setup.py develop
```
This requires setuptools to be installed.
It has no dependencies outside the stadard library so no pip requirements files are needed. 

To test run:
```
python -m unittest discover
```

Usage
--------
The only to functions are merge and merge_versioned. They both take a list of python dicts representing OCDS releases (what you get if you json.loads a release json).

Here is a simple example.
```
import ocdsmerge

releases = [
{
    "ocid": "A",
    "id": "1",
    "date": "2014-01-01",
    "tag": ["tender"],
    "tender": {
        "id": "A",
        "procurementMethod": "Selective"
    }
},
{
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["tender"],
    "tender": {
        "id": "A",
        "procurementMethod": "Open"
    }
}
]

# what goes in an OCDS record under the compiledRelease key
compiledRelease = ocdsmerge.merge(releases)
# what goes in an OCDS record under the versionedRelease key
versionedRelease = ocdsmerge.merge_versioned(releases)
```

This library takes no responsibly in serializing or unserializing the json nor does it help in constructing the rest of the OCDS record.

