import pickle
import pprint
import requests

dictionary = pickle.load(open('../data/inventory_dates.pkl', 'rb'))

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


def get_inv_numbers(year):
    """
    Get the inventory numbers for a range around the given year.
    """
    offsets = 5
    range_years = range(year - offsets, year + offsets)
    inv_numbers = set()

    for y in range_years:
        if y in dictionary:
            for inv_number in dictionary[y]:
                inv_numbers.add(inv_number)
        else:
            print(f"Year {y} not found in dictionary.")

    return list(inv_numbers)


print("Enter a year:")
year = int(input())
inv_numbers = get_inv_numbers(year)
print(f"Inventory numbers for the year {year}: {inv_numbers}")

data = {
    "text": "Gouden AND leeuw",
    "terms": {
        "invNr": inv_numbers
    }
}
response = requests.post(url, headers=headers, params=params, json=data)
print(response.status_code)
pprint.pprint(response.json())
