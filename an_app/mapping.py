MAPPING_FOR_INDEX = {
            "properties": {
                "id": {
                    "type": "integer",
                },
                "text": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
            }
        }
