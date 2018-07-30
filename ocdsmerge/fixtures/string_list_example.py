releases = [
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-01",
        "tag": ["award"],
        "parties": [{
          "id": "consequat reprehenderit",
          "name": "sit Lorem irure proident",
          "roles": ["buyer"]
        }],
    },
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-02",
        "tag": ["award"],
        "parties": [{
          "id": "consequat reprehenderit",
          "name": "new name",
          "roles": ["tenderer"]
        }],
    }
]

compiledRelease = {
    "ocid": "A",
    "id": "1",
    "date": "2014-01-02",
    "tag": ["compiled"],
    "parties": [{
      "id": "consequat reprehenderit",
      "name": "new name",
      "roles": ["tenderer"]
    }],
}

versionedRelease = {
   'ocid': 'A',
   'parties': [{'id': 'consequat reprehenderit',
                'name': [{'releaseDate': '2014-01-01',
                          'releaseID': '1',
                          'releaseTag': ['award'],
                          'value': 'sit Lorem irure proident'},
                         {'releaseDate': '2014-01-02',
                          'releaseID': '1',
                          'releaseTag': ['award'],
                          'value': 'new name'}],
                'roles': [{'releaseDate': '2014-01-01',
                           'releaseID': '1',
                           'releaseTag': ['award'],
                           'value': ['buyer']},
                          {'releaseDate': '2014-01-02',
                           'releaseID': '1',
                           'releaseTag': ['award'],
                           'value': ['tenderer']}]}]
}
