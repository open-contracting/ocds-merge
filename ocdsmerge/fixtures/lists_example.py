
releases = [
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-01",
        "tag": ["award"],
        "parties": [{
          "id": "consequat reprehenderit",
          "additionalIdentifiers": [
            {
              "id": "1",
              "scheme": "aliquip dolor exercitation do",
              "uri": "http://lk.com"
            },
            {
              "id": "2",
              "scheme": "foo",
              "uri": "http://foo.com"
            }
          ],
          "name": "sit Lorem irure proident",
        }],
    },
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-02",
        "tag": ["award"],
        "parties": [{
          "id": "consequat reprehenderit",
          "additionalIdentifiers": [
            {
              "id": "1",
              "scheme": "bar",
            },
            {
              "id": "3",
              "scheme": "aliquip dolor exercitation do",
              "uri": "http://lk.com"
            }
          ],
          "name": "new name",
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
      "additionalIdentifiers": [
        {
          "id": "1",
          "scheme": "bar",
        },
        {
          "id": "3",
          "scheme": "aliquip dolor exercitation do",
          "uri": "http://lk.com"
        }
      ],
      "name": "new name",
    }],
}

versionedRelease = {
   'ocid': 'A',
   'parties': [{'additionalIdentifiers': [{'releaseDate': '2014-01-01',
                                           'releaseID': '1',
                                           'releaseTag': ['award'],
                                           'value': [{'id': '1',
                                                      'scheme': 'aliquip dolor '
                                                                'exercitation do',
                                                      'uri': 'http://lk.com'},
                                                     {'id': '2',
                                                      'scheme': 'foo',
                                                      'uri': 'http://foo.com'}]},
                                          {'releaseDate': '2014-01-02',
                                           'releaseID': '1',
                                           'releaseTag': ['award'],
                                           'value': [{'id': '1', 'scheme': 'bar'},
                                                     {'id': '3',
                                                      'scheme': 'aliquip dolor '
                                                                'exercitation do',
                                                      'uri': 'http://lk.com'}]}],
                'id': 'consequat reprehenderit',
                'name': [{'releaseDate': '2014-01-01',
                          'releaseID': '1',
                          'releaseTag': ['award'],
                          'value': 'sit Lorem irure proident'},
                         {'releaseDate': '2014-01-02',
                          'releaseID': '1',
                          'releaseTag': ['award'],
                          'value': 'new name'}]}]
}
