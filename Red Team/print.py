import pickle
import pprint

file_path = 'q_table.pkl'

with open(file_path, 'rb') as file:
    data = pickle.load(file)
    pprint.pprint(data)
