import numpy as np
import argparse
import os
import pickle
import random

from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.models import load_model

from models import build_block_model
from pygbx.stadium_blocks import STADIUM_BLOCKS
from block_utils import (BID, one_hot_bid, pad_block_sequence)
from config import load_config

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.set_printoptions(suppress=True)

INP_LEN = len(STADIUM_BLOCKS)

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--load', dest='model_filename', metavar='FILE')
parser.add_argument('-n', '--num-tracks', type=int)
parser.add_argument('-d', '--board-dir')
parser.add_argument('-b', '--batch-size', type=int, default=128)
parser.add_argument('-c', '--config', required=True, metavar='FILE')

args = parser.parse_args()
config = load_config(args.config)

batch_size = args.batch_size
lookback = config['lookback']

train_data_file = open(config['train_data'], 'rb')
train_data = pickle.load(train_data_file)
if args.num_tracks:
    train_data = train_data[:args.num_tracks]

def process_entry(blocks, X, y):
    if len(blocks) < lookback:
        return

    for i in range(lookback):
        blocks_in = pad_block_sequence(blocks[:i], lookback)
        block_out = blocks[i]

        X.append([one_hot_bid(block[BID], len(STADIUM_BLOCKS)) for block in blocks_in])
        y.append(one_hot_bid(block_out[BID], len(STADIUM_BLOCKS)))

    for i in range(0, len(blocks) - lookback):
        blocks_in = blocks[i:i + lookback]
        block_out = blocks[i + lookback]

        X.append([one_hot_bid(block[BID], len(STADIUM_BLOCKS)) for block in blocks_in])
        y.append(one_hot_bid(block_out[BID], len(STADIUM_BLOCKS)))


def track_sequence_generator(batch_size):
    while True:
        X = []
        y = []
        while len(X) < batch_size:
            entry = random.choice(train_data)

            blocks = entry[1]
            if len(blocks) > batch_size:
                start = random.randrange(0, len(blocks) - batch_size + 1)
                end = start + batch_size
                blocks = blocks[start:end]

            process_entry(blocks, X, y)

        X = X[:batch_size]
        y = y[:batch_size]
        yield np.reshape(X, ((len(X), lookback, INP_LEN))), np.array(y)

dataset_len = 0
for entry in train_data:
    dataset_len += len(entry[1])

print(f'Dataset size: {dataset_len}')
print(f'Input shape: {(batch_size, lookback, INP_LEN)}')
print(f'Output shape: {len(STADIUM_BLOCKS)}')

gen = track_sequence_generator(batch_size)

callbacks = []
if args.model_filename:
    if os.path.exists(args.model_filename):
        model = load_model(args.model_filename)
    else:
        model = build_block_model(lookback, INP_LEN)

    callbacks.append(ModelCheckpoint(filepath=args.model_filename,
                                     monitor='loss', verbose=1, save_best_only=True, mode='min'))
else:
    model = build_block_model(lookback, INP_LEN)

if args.board_dir:
    callbacks.append(TensorBoard(log_dir=args.board_dir))

model.summary()
history = model.fit_generator(gen, steps_per_epoch=dataset_len / batch_size,
                            epochs=200, callbacks=callbacks)
