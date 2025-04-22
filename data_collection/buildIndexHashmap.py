from bs4 import BeautifulSoup
import re


def extract_years(date_text):
    if date_text == 'z.d':
        return 'unknown'

    clean = re.sub(r'[\[\]\(\)\?]', '', date_text.lower())

    years = re.findall(r'\b(1[5-9]\d{2}|20\d{2})\b', clean)
    years = list(map(int, years))

    if not years:
        centuries = re.findall(r'(\d{1,2})e\b', clean)
        if centuries:
            years = [int(c) * 100 - 100 for c in centuries]

    if not years:
        return None
    elif len(years) == 1:
        return years[0]
    else:
        return (years[0], years[1])


with open('../data/voc_inventory.xml', 'r') as f:
    data = f.read()

output = open('../data/inventory_dates.txt', 'w')

xml_data = BeautifulSoup(data, "xml")

inventory = xml_data.find_all('did')

for entry in inventory:
    entry_number = entry.find('unitid', attrs={'identifier': True})
    if not entry_number:
        continue

    entry_date = entry.find('unitdate')

    # print('number: ' + entry_number.text.strip())

    if entry_date and "normal" in entry_date:
        date = str(extract_years(entry_date['normal']))
    elif entry_date:
        date = str(extract_years(entry_date.text.strip()))
    else:
        date = "unknown"

    line = f"{entry_number.text.strip()}, {date}\n"
    output.write(line)
