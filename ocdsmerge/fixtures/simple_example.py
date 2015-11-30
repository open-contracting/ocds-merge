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

compiledRelease = {
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02", 
    "tag": ["compiled"],
    "tender": {
        "id": "A",
        "procurementMethod": "Open"
    } 
}

versionedRelease = {
    "ocid": "A",
    'tender': 
         {"id": [{"releaseDate": "2014-01-01",
                   "releaseID": "1",
                   "releaseTag": ["tender"],
                   'value': "A"}],

          "procurementMethod": [
           {
                "value": "Selective",
                "releaseDate": "2014-01-01",
                "releaseTag": ["tender"],
                "releaseID": "1"
            },
            {
                "value": "Open",
                "releaseDate": "2014-01-02",
                "releaseTag": ["tender"],
                "releaseID": "2"
            }
        ]
    }
}

