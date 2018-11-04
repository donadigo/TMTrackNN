from keras.models import Input, Model, load_model
from keras.utils import plot_model
from keras.layers.core import Dense, Dropout
from keras.layers import LSTM, Bidirectional, concatenate
from keras.callbacks import ModelCheckpoint

import numpy as np
import pickle
import random
import sys
import argparse

from config import NET_CONFIG
from blocks import BLOCKS, BID, BX, BY, BZ, BROT, EMPTY_BLOCK, one_hot_bid, one_hot_pos, one_hot_rotation, pad_block_sequence
from track_utils import rotate_track_tuples, fit_position_scaler

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

POS_LEN = 3
ROTATE_LEN = 4

INP_LEN = len(BLOCKS) + POS_LEN + ROTATE_LEN

np.set_printoptions(suppress=True)

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--use-generator', dest='usegen',
                    action='store_true', default=False)
parser.add_argument('-l', '--load', dest='model_filename', metavar='FILE')
parser.add_argument('-t', '--tracks', dest='track_num', type=int)

args = parser.parse_args()
if not args.usegen and not args.track_num:
    print('Not specifying number of tracks processed without using generator is forbidden.')
    quit()

batch_size = NET_CONFIG['batch_size']
lookback = NET_CONFIG['lookback']

train_data_file = open(NET_CONFIG['train_fname'], 'rb')
train_data = pickle.load(train_data_file)
if args.track_num:
    train_data = train_data[:args.track_num]

scaler = fit_position_scaler(train_data)


def block_to_vec(block, encode_pos=True):
    if block[0] == 0:
        return [0] * INP_LEN

    bid_vec = one_hot_bid(block[0])
    if encode_pos:
        pos_vec = scaler.transform([block[BX:BZ+1]])[0]
        rot_vec = one_hot_rotation(block[4])
    else:
        pos_vec = [-1, -1, -1]
        rot_vec = [-1, -1, -1, -1]

    return bid_vec + list(pos_vec) + rot_vec


def append_blocks(blocks_in, block_out, X, y_pos, y_rot):
    end_idx = len(blocks_in) - 1
    X.append([block_to_vec(block, i != end_idx)
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
            blocks = rotate_track_tuples(entry[1], r)
            process_entry(blocks, X, y_pos, y_rot)

        start = random.randrange(0, len(X) - batch_size + 1)
        end = start + batch_size

        X = np.reshape(X[start:end], (batch_size, lookback, INP_LEN))
        y_pos = np.array(y_pos[start:end])
        y_rot = np.array(y_rot[start:end])
        yield X, [y_pos, y_rot]


def build_model():
    inp = Input(shape=(lookback, INP_LEN))

    x = Bidirectional(LSTM(512, return_sequences=True))(inp)
    x = Dropout(0.2)(x)

    x = Bidirectional(LSTM(256, return_sequences=True))(x)
    x = Dropout(0.2)(x)

    x = Bidirectional(LSTM(256))(x)
    x = Dropout(0.2)(x)

    pos = Dense(3, activation='linear', name='pos')(x)
    rot = Dense(4, activation='softmax', name='rot')(x)

    model = Model(inputs=inp, outputs=[pos, rot])
    model.compile(loss=['mse', 'categorical_crossentropy'],
                  optimizer='rmsprop')
    return model


if not args.usegen:
    X = []
    y_pos = []
    y_rot = []

    for track in train_data:
        process_entry(track[1], X, y_pos, y_rot)

    X = np.reshape(X, (len(X), lookback, INP_LEN))
    y_pos = np.array(y_pos)
    y_rot = np.array(y_rot)

    print('Input shape: {}'.format(X.shape))
    print('Output shape: {}, {}'.format(y_pos.shape, y_rot.shape))
else:
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
    model = load_model(args.model_filename)
    callbacks.append(ModelCheckpoint(filepath=args.model_filename,
                                     monitor='loss', verbose=1, save_best_only=True, mode='min'))
else:
    model = build_model()

model.summary()
if args.usegen:
    history = model.fit_generator(
        gen, steps_per_epoch=dataset_len / batch_size, epochs=200, callbacks=callbacks)
else:
    history = model.fit(X, [y_pos, y_rot], batch_size=batch_size,
                        epochs=200, verbose=1, callbacks=callbacks)
