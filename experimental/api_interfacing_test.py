import requests
import pprint

url = "https://gloccoli.tt.di.huc.knaw.nl/projects/globalise/search"

params = {
    "indexName": "docs-2024-03-18",
    "from": 0,
    "size": 10,
    "fragmentSize": 100,
    "sortBy": "_score",
    "sortOrder": "DESC"
}

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

data = {
    "text": "Gouden AND leeuw",
    "terms": {
        "invNr": ["1102"]
    }
}

response = requests.post(url, headers=headers, params=params, json=data)
print(response.status_code)
pprint.pprint(response.json())
