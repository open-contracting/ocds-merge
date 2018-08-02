releases = [
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-01",
        "tag": ["tender"],
        "tender": {
            "id": "A",
            "items": [{
                "id": "item1",
                "unit": {"id": "unit_id"}
            }]
        }
    },
    {
        "ocid": "A",
        "id": "2",
        "date": "2014-01-02",
        "tag": ["tender"],
        "tender": {
            "id": "A",
            "items": [{
                "id": "item1",
                "unit": {"id": "unit_id_2"}
            }]
        }
    }
]

compiledRelease = {
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["compiled"],
    "tender": {
        "id": "A",
        "items": [{
            "id": "item1",
            "unit": {"id": "unit_id_2"}
        }]
    }
}

versionedRelease = {
    'ocid': 'A',
    'tender': {'id': [{'releaseDate': '2014-01-01',
                       'releaseID': '1',
                       'releaseTag': ['tender'],
                       'value': 'A'}],
               'items': [{'id': 'item1',
                          'unit': {'id': [{'releaseDate': '2014-01-01',
                                           'releaseID': '1',
                                           'releaseTag': ['tender'],
                                           'value': 'unit_id'},
                                          {'releaseDate': '2014-01-02',
                                           'releaseID': '2',
                                           'releaseTag': ['tender'],
                                           'value': 'unit_id_2'}]}}
                         ]
               }
}
