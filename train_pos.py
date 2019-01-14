from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.models import load_model

import numpy as np
import pickle
import random
import sys
import argparse

from models import build_pos_model
from core.stadium_blocks import STADIUM_BLOCKS
from core.block_utils import BID, BX, BY, BZ, BROT, EMPTY_BLOCK, BFLAGS, one_hot_rotation, pad_block_sequence, block_to_vec
from core.track_utils import rotate_track_tuples, fit_data_scaler, vectorize_track
from config import load_config

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.set_printoptions(suppress=True)

POS_LEN = 3
ROTATE_LEN = 4
INP_LEN = len(STADIUM_BLOCKS) + POS_LEN + ROTATE_LEN

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

scaler = fit_data_scaler(train_data)

def append_blocks(blocks_in, block_out, X, y_pos, y_rot):
    end_idx = len(blocks_in) - 1
    X.append([block_to_vec(block, INP_LEN, len(STADIUM_BLOCKS), scaler, i != end_idx)
              for i, block in enumerate(blocks_in)])
    y_pos.append(block_out[BX:BZ+1])
    y_rot.append(one_hot_rotation(block_out[BROT]))


def process_entry(blocks, X, y_pos, y_rot):
    if len(blocks) < lookback:
        return

    for i in range(1, lookback):
        blocks_in = pad_block_sequence(blocks[:i], lookback)
        block_out = blocks[i - 1]
        append_blocks(blocks_in, block_out, X, y_pos, y_rot)

    for i in range(0, len(blocks) - lookback + 1):
        blocks_in = blocks[i:i + lookback]
        block_out = blocks[i + lookback - 1]
        append_blocks(blocks_in, block_out, X, y_pos, y_rot)


def track_sequence_generator(batch_size):
    while True:
        X = []
        y_pos = []
        y_rot = []
        while len(X) < batch_size:
            entry = random.choice(train_data)
            r = random.randrange(0, 4)
            if r == 0:
                blocks = entry[1]
            else:
                blocks = rotate_track_tuples(entry[1], r)

            blocks = vectorize_track(blocks)
            if len(blocks) > batch_size:
                start = random.randrange(0, len(blocks) - batch_size + 1)
                end = start + batch_size
                blocks = blocks[start:end]

            process_entry(blocks, X, y_pos, y_rot)

        X = np.reshape(X[:batch_size], (batch_size, lookback, INP_LEN))
        y_pos = np.array(y_pos[:batch_size])
        y_rot = np.array(y_rot[:batch_size])

        yield X, [y_pos, y_rot]

dataset_len = 0
for entry in train_data:
    dataset_len += len(entry[1])

dataset_len *= 4

print('Dataset size: {}'.format(dataset_len))
print('Input shape: {}'.format((batch_size, lookback, INP_LEN)))
print('Output shape: {}'.format((3, 4)))

gen = track_sequence_generator(batch_size)

callbacks = []
if args.model_filename:
    if os.path.exists(args.model_filename):
        model = load_model(args.model_filename)
    else:
        model = build_pos_model(lookback, INP_LEN)

    callbacks.append(ModelCheckpoint(filepath=args.model_filename,
                                     monitor='loss', verbose=1, save_best_only=True, mode='min'))
else:
    model = build_pos_model(lookback, INP_LEN)

if args.board_dir:
    callbacks.append(TensorBoard(log_dir=args.board_dir))

model.summary()
history = model.fit_generator(gen, steps_per_epoch=dataset_len / batch_size,
                            epochs=200, callbacks=callbacks)