from bs4 import BeautifulSoup
import pickle
import re


# Uses regex to extract the years from the date text.
def extract_years(date_text):
    if date_text == 'z.d':
        return None

    clean = re.sub(r'[\[\]\(\)\?]', '', date_text.lower())

    years = re.findall(r'\b(1[5-9]\d{2}|20\d{2})\b', clean)
    years = list(map(int, years))

    if not years:
        centuries = re.findall(r'(\d{1,2})e\b', clean)

        if centuries:
            years = [int(c) * 100 - 100 for c in centuries]

    for year in years:
        if year < 1500:
            years.remove(year)

    if not years:
        return None
    elif len(years) == 1:
        return years[0]
    else:
        return (years[0], years[1])


with open('../data/voc_inventory.xml', 'r') as f:
    data = f.read()

output = open('../data/inventory_dates.txt', 'w')

dictionary = {}

xml_data = BeautifulSoup(data, "xml")
inventory = xml_data.find_all('did')

# Saves each entry into a file and into the dictionary.
for entry in inventory:
    entry_number = entry.find('unitid', attrs={'identifier': True})
    if not entry_number:
        continue

    entry_date = entry.find('unitdate')

    if entry_date and "normal" in entry_date:
        date = extract_years(entry_date['normal'])
    elif entry_date:
        date = extract_years(entry_date.text.strip())
    else:
        date = None

    dates = []
    if type(date) is tuple:
        if date[0] < date[1]:
            dates = list(range(date[0], date[1] + 1))
        else:
            dates = list(range(date[1], date[0] + 1))

    elif date is not None:
        dates = [date]

    for x in dates:
        if x not in dictionary:
            dictionary[x] = []
        dictionary[x].append(entry_number.text.strip())

    line = f"{entry_number.text.strip()}, {date}\n"
    output.write(line)

# Saves the dictionary to a file
with open('../data/inventory_dates.pkl', 'wb') as file:
    pickle.dump(dictionary, file)
