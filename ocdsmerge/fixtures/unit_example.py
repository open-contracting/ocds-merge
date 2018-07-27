releases = [
    {
        "ocid": "A",
        "id": "1",
        "date": "2014-01-01",
        "tag": ["tender"],
        "tender": {
            "id": "A",
            "items": [{
                "id" : "item1",
                "unit" : {"id": "EA",
                         "scheme":"UNCEFACT",
                         "name":"Each"}
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
                "id" : "item1",
                "unit" : {"id": "TNE",
                         "scheme":"UNCEFACT"
                         }
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
            "id" : "item1",
            "unit" : {"id": "TNE",
                      "scheme":"UNCEFACT"
                     }
        }]
    }
}

versionedRelease = {
    'ocid': 'A',
    'tender': {
          'id': [
            {
              'releaseDate': '2014-01-11T00:00:00Z',
              'releaseID': '1',
              'releaseTag': [
                'tender'
              ],
              'value': 'A'
            }
          ],
          'items': [
            {
              'id': 'item1',
              'unit': [
                {
                  'releaseDate': '2014-01-01T00:00:00Z',
                  'releaseID': '1',
                  'releaseTag': [
                    'tender'
                  ],
                  'value': {
                    'id': 'EA',
                    'scheme': 'UNCEFACT',
                    'name': 'Each'
                  }
                },
                {
                  'releaseDate': '2014-01-02T00:00:00Z',
                  'releaseID': '2',
                  'releaseTag': [
                    'tender'
                  ],
                  'value': {
                    'id': 'TNE',
                    'scheme': 'UNCEFACT'
                  }
                }
              ]
            }
          ]
        }
}

