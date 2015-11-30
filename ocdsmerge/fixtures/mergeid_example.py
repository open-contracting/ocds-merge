releases = [
{
    "ocid": "A",
    "id": "1",
    "date": "2014-01-01",
    "tag": ["tender"],
    "tender": {
        "items": [
            {
                "id": "1",
                "description": "Item 1",
                "quantity": 1
            },
            {
                "id": "2",
                "description": "Item 2",
                "quantity": 1
            }
        ]
    }
},
{
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["tender"],
    "tender": {
        "items": [
            {
                "id": "1",
                "description": "Item 1",
                "quantity": 2
            },
            {
                "id": "3",
                "description": "Item 3",
                "quantity": 1
            }
        ]
    }
}
]

compiledRelease = {
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["compiled"],
    "tender": {
        "items": [
            {
                "id": "1",
                "description": "Item 1",
                "quantity": 2
            },
            {
                "id": "2",
                "description": "Item 2",
                "quantity": 1
            },
            {
                "id": "3",
                "description": "Item 3",
                "quantity": 1
            }
        ]
    }
}

versionedRelease = {
    "ocid": "A",
    "tender": {
        "items": [
            {
                "id": "1",
                "description": [
                    {
                        "value": "Item 1",
                        "releaseDate": "2014-01-01",
                        "releaseTag": ["tender"],
                        "releaseID": "1"
                    }
                ],
                "quantity": [
                    {
                        "value": 1,
                        "releaseDate": "2014-01-01",
                        "releaseTag": ["tender"],
                        "releaseID": "1"
                    },
                    {
                        "value": 2,
                        "releaseDate": "2014-01-02",
                        "releaseTag": ["tender"],
                        "releaseID": "2"
                    }
                ]
            },
            {
                "id": "2",
                "description": [
                    {
                        "value": "Item 2",
                        "releaseDate": "2014-01-01",
                        "releaseTag": ["tender"],
                        "releaseID": "1"
                    }
                ],
                "quantity": [
                    {
                        "value": 1,
                        "releaseDate": "2014-01-01",
                        "releaseTag": ["tender"],
                        "releaseID": "1"
                    },
                ]
            },
            {
                "id": "3",
                "description": [
                    {
                        "value": "Item 3",
                        "releaseDate": "2014-01-02",
                        "releaseTag": ["tender"],
                        "releaseID": "2"
                    }
                ],
                "quantity": [
                    {
                        "value": 1,
                        "releaseDate": "2014-01-02",
                        "releaseTag": ["tender"],
                        "releaseID": "2"
                    },
                ]
            }
        ]
    }
}

