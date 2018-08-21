import pickle
from blocks import *

# logging.basicConfig(level=logging.DEBUG)
train_data_file = open('train-data.bin', 'r')
train_data = pickle.load(train_data_file)

blocks = 0
for i in range(len(train_data)):
    if len(train_data[i][1]) < 20:
        del train_data[i]
        print('DELET')
    else:
        blocks += len(train_data[i][1])

print(blocks)

    