from keras.models import Sequential, Input, Model, load_model
from keras.utils import plot_model
from keras.layers.core import Dense, Dropout
from keras.layers import LSTM, Bidirectional
from keras.callbacks import ModelCheckpoint

import numpy as np 
import pickle
import random
import sys
import argparse

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.set_printoptions(suppress=True)

from config import NET_CONFIG
from blocks import BLOCKS, BID, BX, BY, BZ, BROT, EMPTY_BLOCK, EDITOR_IDS
from blocks import one_hot_bid, one_hot_pos, one_hot_rotation, pad_block_sequence
from builder import Builder

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

train_data_file = open(NET_CONFIG['train_fname'], 'rb')
train_data = pickle.load(train_data_file)
if args.track_num:
    train_data = train_data[:args.track_num]

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def generate_block_seq(model, blen):
    X = np.zeros((1, lookback, len(BLOCKS)))
    for _ in range(blen):
        preds = model.predict(X)
        bid = sample(preds[0]) + 1
        try:
            eid = EDITOR_IDS[bid]
        except KeyError:
            continue
        print(eid)

        for i in range(1, lookback):
            X[0][i - 1] = X[0][i]

        X[0][-1] = one_hot_bid(bid)

def process_entry(blocks, X, y):
    if len(blocks) < lookback:
        return

    for i in range(lookback):
        blocks_in = pad_block_sequence(blocks[:i], lookback)
        block_out = blocks[i]

        X.append([one_hot_bid(block[0]) for block in blocks_in])
        y.append(one_hot_bid(block_out[0]))

    for i in range(0, len(blocks) - lookback):
        blocks_in = blocks[i:i + lookback]
        block_out = blocks[i + lookback]

        X.append([one_hot_bid(block[0]) for block in blocks_in])
        y.append(one_hot_bid(block_out[0]))

def track_sequence_generator(batch_size):
    while True:
        X = []
        y = []
        while len(X) < batch_size:
            entry = random.choice(train_data)
            process_entry(entry[1], X, y)
        
        X = X[:batch_size]
        y = y[:batch_size]
        yield np.reshape(X, ((len(X), lookback, len(BLOCKS)))), np.array(y)

def build_model():
    model = Sequential()
    model.add(LSTM(300, return_sequences=True, input_shape=(lookback, len(BLOCKS))))
    model.add(Dropout(0.3))
    model.add(LSTM(300, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(Dense(len(BLOCKS), activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    return model

if not args.usegen:
    print('Preparing train data...')
    
    dataX = []
    dataY = []

    i = 0
    for entry in train_data:
        print(f'\t-- Preparing sequence {i}: {entry[0]}')
        process_entry(entry[1], dataX, dataY)
        i += 1

    X = np.reshape(dataX, (len(dataX), lookback, len(BLOCKS)))
    y = np.array(dataY)

    del dataX
    del dataY

    print(f'Input data shape: {X.shape}')
    print(f'Output data shape: {y.shape}')
else:
    dataset_len = 0
    for entry in train_data:
        dataset_len += len(entry[1])

    print(f'Dataset size: {dataset_len}')
    print(f'Input shape: {(batch_size, lookback, len(BLOCKS))}')
    print(f'Output shape: {len(BLOCKS)}')

gen = track_sequence_generator(batch_size)

callbacks = []
if args.model_filename:
    model = load_model(args.model_filename)
    callbacks.append(ModelCheckpoint(filepath=args.model_filename, monitor='loss', verbose=1, save_best_only=True, mode='min'))
else:
    model = build_model()

model.summary()
if args.usegen:
    history = model.fit_generator(gen, steps_per_epoch=dataset_len / batch_size, epochs=200, callbacks=callbacks)
else:
    history = model.fit(X, y, batch_size=128, epochs=100, verbose=1, shuffle=True, callbacks=callbacks)