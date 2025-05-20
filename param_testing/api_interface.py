import requests
import re

url = "https://gloccoli.tt.di.huc.knaw.nl/projects/globalise/search"

PARAMS = {
    "indexName": "docs-2024-03-18",
    "from": 0,
    "size": 10,
    "fragmentSize": 50,
    "sortBy": "_score",
    "sortOrder": "DESC"
}

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}


def return_requests(text, inv_numbers, size=50):
    """
    Return the requests for a given year range.
    """
    data = {
        "text": text,
        "terms": {
            "invNr": inv_numbers
        }
    }

    results = []
    print(f"Requesting block: {PARAMS['from']} to {PARAMS['from'] + PARAMS['size']}.")
    response = requests.post(url, headers=HEADERS, params=PARAMS, json=data)
    response_json = response.json()
    total_results = response_json['total']['value']

    print(f"Total results: {total_results}")

    if total_results == 0:
        print("No results found.")
        return results

    results += response_json['results']

    while PARAMS['from'] + PARAMS['size'] < min(total_results, 200):
        PARAMS['from'] += PARAMS['size']
        print(f"Requesting block: {PARAMS['from']} to {PARAMS['from'] + PARAMS['size']}.")
        response = requests.post(url, headers=HEADERS, params=PARAMS, json=data)
        response_json = response.json()
        results += response_json['results']

    print(f"Results:\n{results}")

    return clean_output(results)


def clean_text(text):
    """
    Clean the text by concatenating the list, removing HTML tags, and stripping non-alphabetic characters.
    """
    if not isinstance(text, list):
        return None

    text = ' '.join(text)
    text = text.replace("<em>", "").replace("</em>", "").rstrip("\n")
    # text = re.sub(r'[^a-zA-Z\s]', '', text)

    return text


def clean_output(results):
    """
    Clean the output of the results.
    """
    cleaned_results = []
    for result in results:
        cleaned_result = {
            "text": clean_text(result['_hits']['text']),
            "id": result['_id'],
            "document": result['document'],
            "invNr": result['invNr'],
        }
        cleaned_results.append(cleaned_result)
    return cleaned_results
