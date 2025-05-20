from api_interface import return_requests
import pickle
import re
import csv

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


def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text)


if __name__ == "__main__":
    original_text = clean_text(
        "de Gouden Leeuw  is onbequaem bevonden omme met retouren naer ’t " \
        "vaderlandt over te gaen, jaa is inwendich soo vergaen, dat, " \
        "onaengesyen de handt daer extra-ordinaris aengehouden is, niet " \
        "langer in ’t vaerwater sal connen continueren.")
    selected_entity = "Gouden AND leeuw"
    year = 1633

    print(f"\nSearching for: {selected_entity}")
    print(f"Year: {year}")
    print(f"Inventory Numbers: {get_inv_numbers(year)}\n")

    request_results = return_requests(
        selected_entity, get_inv_numbers(year), len(original_text))
    texts = [result['text'] for result in request_results if 'text' in result]

    with open("Gouden_Leeuw.csv", mode="w", encoding="utf-8", newline="") as csvfile:
        if request_results:
            fieldnames = request_results[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in request_results:
                writer.writerow(result)
            print(
                f"Written {len(request_results)} entries to request_results.csv")
        else:
            print("No results to write.")
