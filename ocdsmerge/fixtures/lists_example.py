
releases = [
{
    "ocid": "A",
    "id": "1",
    "date": "2014-01-01",
    "tag": ["award"],
    "awards": [
        {
            "id": 1,
            "suppliers": [
                {
                    "name": "Supplier 1",
                    "address": {
                        "countryName": "Canada"
                    }
                },
                {
                    "name": "Supplier 2",
                    "address": {
                        "countryName": "Canada"
                    }
                }
            ]
        }
    ]
},
{
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["award"],
    "awards": [
        {
            "id": 1,
            "suppliers": [
                {
                    "name": "Supplier 1",
                    "address": {
                        "countryName": "Canada"
                    }
                },
                {
                    "name": "Supplier 2",
                    "address": {
                        "countryName": "United Kingdom"
                    }
                }
            ]
        }
    ]
}
]

compiledRelease = {
    "ocid": "A",
    "id": "2",
    "date": "2014-01-02",
    "tag": ["compiled"],
    "awards": [
        {
            "id": 1,
            "suppliers": [
                {
                    "name": "Supplier 1",
                    "address": {
                        "countryName": "Canada"
                    }
                },
                {
                    "name": "Supplier 2",
                    "address": {
                        "countryName": "United Kingdom"
                    }
                }
            ]
        }
    ]
}

versionedRelease = {
    "ocid": "A",
    "awards": [
        {
            "id": 1,
            "suppliers": [
                {
                    "value": [
                        {
                            "name": "Supplier 1",
                            "address": {
                                "countryName": "Canada"
                            }
                        },
                        {
                            "name": "Supplier 2",
                            "address": {
                                "countryName": "Canada"
                            }
                        }
                    ],
                    "releaseDate": "2014-01-01",
                    "releaseTag": ["award"],
                    "releaseID": "1"
                },
                {
                    "value": [
                        {
                            "name": "Supplier 1",
                            "address": {
                                "countryName": "Canada"
                            }
                        },
                        {
                            "name": "Supplier 2",
                            "address": {
                                "countryName": "United Kingdom"
                            }
                        }
                    ],
                    "releaseDate": "2014-01-02",
                    "releaseTag": ["award"],
                    "releaseID": "2"
                }
            ]
        }
    ]
} 

