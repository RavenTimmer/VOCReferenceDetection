import pickle
import pprint

from api_interface import return_requests


dictionary = pickle.load(open('../data/inventory_dates.pkl', 'rb'))


def get_inv_numbers(year):
    """
    Get the inventory numbers for a range around the given year.
    """
    offsets = 1
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

request = return_requests("Gouden AND leeuw", inv_numbers)
pprint.pprint(request)
