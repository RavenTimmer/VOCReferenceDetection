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
        "zo is dat een en ander van die efficatie geweest dat de finale dispositie daarover is gesurcheert gebleven tot 30e daaraanvolgende , als wanneer Zijn Edelheyt desselvs zo even aangehaalde intentie wederom ten tapijte , en na het ingekomen advijs van den heere gouverneur-generaal Thedens de zake zooverre gebragt heeft , datter alsdoen g’arresteert is hem per het schip Amsterdam op den 6e november te laten vertrecken , en bij erlanginge van eenig favorabel berigt wegens den Javasen krijg (dog anders niet ) de Oude Zijp tot geselschap mede te geven , invoegen als den heere Valckenier op dien gestipuleerden dag dan ook met voormelte Amsterdam alleen de reyse van dese rheede ondernomen en het generalaat in behoorlijke forma aan desselvs successeur , den presenten heere gouverneur-generaal Johannes Thedens")
    selected_entity = "Johannes AND Thedens"
    year = 1742

    print(f"\nSearching for: {selected_entity}")
    print(f"Year: {year}")
    print(f"Inventory Numbers: {get_inv_numbers(year)}\n")

    request_results = return_requests(
        selected_entity, get_inv_numbers(year), len(original_text))
    texts = [result['text'] for result in request_results if 'text' in result]

    with open("Johannes_Thedens.csv", mode="w", encoding="utf-8", newline="") as csvfile:
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
