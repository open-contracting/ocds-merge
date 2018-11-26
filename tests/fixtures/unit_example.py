releases = [
  {
    "ocid": "A",
    "id": "1",
    "date": "2014-01-01T00:00:00Z",
    "tag": [
      "tender"
    ],
    "tender": {
      "id": "A",
      "items": [
        {
          "id": "item1",
          "unit": {
            "id": "EA",
            "scheme": "UNCEFACT",
            "name": "Each"
          }
        }
      ]
    }
  },
  {
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02T00:00:00Z",
    "tag": [
      "tender"
    ],
    "tender": {
      "id": "A",
      "items": [
        {
          "id": "item1",
          "unit": {
            "id": "TNE",
            "scheme": "UNCEFACT"
          }
        }
      ]
    }
  }
]

compiledRelease = {
  "ocid": "A",
  "id": "2",
  "date": "2014-01-02T00:00:00Z",
  "tag": [
    "compiled"
  ],
  "tender": {
    "id": "A",
    "items": [
      {
        "id": "item1",
        "unit": {
          "id": "TNE",
          "name": "Each",
          "scheme": "UNCEFACT"
        }
      }
    ]
  }
}

versionedRelease = {
  'ocid': 'A',
  'tender': {
    'id': [
      {
        'releaseDate': '2014-01-01T00:00:00Z',
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
        'unit': {
          'id': [
            {
              'releaseDate': '2014-01-01T00:00:00Z',
              'releaseID': '1',
              'releaseTag': [
                'tender'
              ],
              'value': 'EA'
            },
            {
              'releaseDate': '2014-01-02T00:00:00Z',
              'releaseID': '2',
              'releaseTag': [
                'tender'
              ],
              'value': 'TNE'
            }
          ],
          'name': [
            {
              'releaseDate': '2014-01-01T00:00:00Z',
              'releaseID': '1',
              'releaseTag': [
                'tender'
              ],
              'value': 'Each'
            }
          ],
          'scheme': [
            {
              'releaseDate': '2014-01-01T00:00:00Z',
              'releaseID': '1',
              'releaseTag': [
                'tender'
              ],
              'value': 'UNCEFACT'
            }
          ]
        }
      }
    ]
  }
}
