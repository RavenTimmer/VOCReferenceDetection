import pickle

dictionary = pickle.load(open('../data/inventory_dates.pkl', 'rb'))

for key in dictionary:
    print(f"Year: {key}, Count: {len(dictionary[key])}")
