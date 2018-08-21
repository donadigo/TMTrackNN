from keras.models import Input, Model, load_model
from keras.utils import plot_model
from keras.layers.core import Dense, Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint

import numpy as np 
import pickle
import random
import sys
import argparse

from config import NET_CONFIG
from blocks import BLOCKS, BID, BX, BY, BZ, BROT, EMPTY_BLOCK, one_hot_bid, one_hot_pos, one_hot_rotation, pad_block_sequence
from builder import Builder

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

POS_LEN = 3
ROTATE_LEN = 4

INP_LEN = len(BLOCKS) + (32 * POS_LEN) + ROTATE_LEN

np.set_printoptions(suppress=True)

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--use-generator', dest='usegen', action='store_true', default=False)
parser.add_argument('-l', '--load', dest='model_filename', metavar='FILE')
parser.add_argument('-t', '--tracks', dest='track_num', type=int)

args = parser.parse_args()
if not args.usegen and not args.track_num:
    print('Not specifying number of tracks processed without using generator is forbidden.')
    quit()

batch_size = NET_CONFIG['batch_size']
lookback = NET_CONFIG['lookback']

train_data_file = open(NET_CONFIG['train_fname'], 'r')
train_data = pickle.load(train_data_file)
if args.track_num:
    train_data = train_data[:args.track_num]

block_model = load_model('models/block-model.h5')

def block_to_vec(block, encode_pos=True):
    if block[0] == 0:
        return [0] * INP_LEN

    bid_vec = one_hot_bid(block[0])
    if encode_pos:
        pos_vec = one_hot_pos(block[BX]) + one_hot_pos(block[BY], 1) + one_hot_pos(block[BZ])
        rot_vec = one_hot_rotation(block[4])
    else:
        pos_vec = [0] * (POS_LEN * 32)
        rot_vec = [0] * ROTATE_LEN

    return bid_vec + list(pos_vec) + rot_vec

def append_blocks(blocks_in, block_out, X, y_pos_x, y_pos_y, y_pos_z, y_rot):
    end_idx = len(blocks_in) - 1
    X.append([block_to_vec(block, i != end_idx) for i, block in enumerate(blocks_in)])
    y_pos_x.append(one_hot_pos(block[BX]))
    y_pos_y.append(one_hot_pos(block[BY], 1))
    y_pos_z.append(one_hot_pos(block[BZ]))
    y_rot.append(one_hot_rotation(block_out[BROT]))

def process_entry(blocks, X, y_pos_x, y_pos_y, y_pos_z, y_rot):
    if len(blocks) < lookback:
        return

    for i in range(1, lookback):
        blocks_in = pad_block_sequence(blocks[:i], lookback)
        block_out = blocks[i - 1]
        append_blocks(blocks_in, block_out, X, y_pos_x, y_pos_y, y_pos_z, y_rot)

    for i in range(0, len(blocks) - lookback + 1):
        blocks_in = blocks[i:i + lookback]
        block_out = blocks[i + lookback - 1]
        append_blocks(blocks_in, block_out, X, y_pos_x, y_pos_y, y_pos_z, y_rot)

def track_sequence_generator(batch_size):
    while True:
        X = []
        y_pos_x = []
        y_pos_y = []
        y_pos_z = []
        y_rot = []
        while len(X) < batch_size:
            entry = random.choice(train_data)
            process_entry(entry[1], X, y_pos_x, y_pos_y, y_pos_z, y_rot)
        
        X = np.reshape(X[:batch_size], (batch_size, lookback, INP_LEN))
        y_pos_x = np.array(y_pos_x[:batch_size])
        y_pos_y = np.array(y_pos_y[:batch_size])
        y_pos_z = np.array(y_pos_z[:batch_size])
        y_rot = np.array(y_rot[:batch_size])
        yield X, [y_pos_x, y_pos_y, y_pos_z, y_rot]


def build_model():
    inp = Input(shape=(lookback, INP_LEN))
    x = LSTM(200, return_sequences=True)(inp)
    x = Dropout(0.3)(x)
    x = LSTM(200)(x)
    x = Dropout(0.3)(x)
    pos_x = Dense(32, activation='softmax', name='pos_x')(x)
    pos_y = Dense(32, activation='softmax', name='pos_y')(x)
    pos_z = Dense(32, activation='softmax', name='pos_z')(x)
    rot = Dense(4, activation='softmax', name='rot')(x)

    model = Model(inputs=inp, outputs=[pos_x, pos_y, pos_z, rot])
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    return model

if not args.usegen:
    X = []
    y_pos_x = []
    y_pos_y = []
    y_pos_z = []
    y_rot = []

    for track in train_data:
        process_entry(track[1], X, y_pos_x, y_pos_y, y_pos_z, y_rot)

    X = np.reshape(X, (len(X), lookback, INP_LEN))
    y_pos_x = np.array(y_pos_x)
    y_pos_y = np.array(y_pos_y)
    y_pos_z = np.array(y_pos_z)
    y_rot = np.array(y_rot)

    print('Input shape: {}'.format(X.shape))
    print('Output shape: {}, {}, {}, {}'.format(y_pos_x.shape, y_pos_y.shape, y_pos_z.shape, y_rot.shape))
else:
    dataset_len = 0
    for entry in train_data:
        dataset_len += len(entry[1])

    print('Dataset size: {}'.format(dataset_len))
    print('Input shape: {}'.format((batch_size, lookback, INP_LEN)))
    print('Output shape: {}, {}'.format((POS_LEN, 32), (1, ROTATE_LEN)))
    
gen = track_sequence_generator(batch_size)
# checkpoint = ModelCheckpoint(filepath='models/position-model.h5', monitor='loss', verbose=1, save_best_only=True, mode='min')

if args.model_filename:
    model = load_model(args.model_filename)
    model.summary()
    b = Builder(block_model, model, None, lookback, train_data, True)
else:
    model = build_model()
    model.summary()

    if args.usegen:
        history = model.fit_generator(gen, steps_per_epoch=dataset_len / batch_size, epochs=200)
    else:
        history = model.fit(X, [y_pos_x, y_pos_y, y_pos_z, y_rot], batch_size=batch_size, epochs=200, verbose=1)
