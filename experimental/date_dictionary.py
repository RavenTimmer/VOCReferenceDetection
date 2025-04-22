import pickle

with open('../data/inventory_dates.pkl', 'rb') as file:
    loaded_data = pickle.load(file)

print(loaded_data)
