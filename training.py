from keras.models import Sequential, Input, Model, load_model
from keras.utils import plot_model
from keras.layers.core import Dense, Dropout, Flatten, Lambda
from keras.optimizers import RMSprop
from keras.layers import LSTM
from keras.utils import Sequence
from keras import backend as K
import numpy as np 
import pickle
import random
import sys
import argparse
from blocks import vectorize_block, EMPTY_BLOCK, INPUT_LEN, OUTPUT_LEN
from builder import Builder

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
np.set_printoptions(suppress=True)

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--use-generator', dest='usegen', action='store_true', default=False)
parser.add_argument('-l', '--load', dest='model_filename', metavar='FILE')
parser.add_argument('-t', '--tracks', dest='track_num', type=int)

args = parser.parse_args()

batch_size = 128
lookback = 20

train_data_file = open('train-data.bin', 'r')
train_data = pickle.load(train_data_file)
if args.track_num:
    train_data = train_data[:args.track_num]

def build_track(model, track_len, use_seed=False, seed_length=3, seed_idx=-1):
    builder = Builder(model, lookback, train_data)
    return builder.build(track_len, use_seed=use_seed, seed_length=seed_length, save_path='generated-track.bin', seed_idx=seed_idx)

def pad_block_sequence(seq, maxlen):
    pad = [EMPTY_BLOCK] * (maxlen - len(seq))
    return pad + seq

def process_entry(blocks, X, y):
    if len(blocks) < lookback:
        return

    for i in range(lookback):
        blocks_in = pad_block_sequence(blocks[:i], lookback)
        block_out = blocks[i]

        X.append([vectorize_block(block, True) for block in blocks_in])
        y.append(vectorize_block(block_out, False))

    for i in range(0, len(blocks) - lookback):
        blocks_in = blocks[i:i + lookback]
        block_out = blocks[i + lookback]

        X.append([vectorize_block(block, True) for block in blocks_in])
        y.append(vectorize_block(block_out, False))
    
def track_sequence_generator(batch_size):
    while True:
        X = []
        y = []
        while len(X) < batch_size:
            entry = random.choice(train_data)
            process_entry(entry[1], X, y)
        
        X = X[:batch_size]
        y = y[:batch_size]
        yield np.reshape(X, ((len(X), lookback, INPUT_LEN))), np.array(y)

# From https://blog.manash.me/multi-task-learning-in-keras-implementation-of-multi-task-classification-loss-f1d42da5c3f6
def multitask_loss(y_true, y_pred):
    y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
    return K.mean(K.sum(- y_true * K.log(y_pred) - (1 - y_true) * K.log(1 - y_pred), axis=1))


if not args.usegen:
    print('Preparing train data...')
    
    dataX = []
    dataY = []
    i = 0
    for entry in train_data:
        print('\t-- Preparing sequence {}: {}'.format(i, entry[0]))
        process_entry(entry[1], dataX, dataY)
        i += 1

    X = np.reshape(dataX, (len(dataX), lookback, INPUT_LEN))
    y = np.array(dataY)

    del dataX
    del dataY

    print('Input data shape: {}'.format(X.shape))
    print('Output data shape: {}'.format(y.shape))
else:
    dataset_len = 0
    for entry in train_data:
        dataset_len += len(entry[1])

    print('Dataset size: {}'.format(dataset_len))

gen = track_sequence_generator(batch_size)

if args.model_filename:
    model = load_model(args.model_filename, custom_objects={ 'multitask_loss' : multitask_loss })
    model.summary()
else:
    inputs = Input(shape=(lookback, INPUT_LEN))
    x = LSTM(400, return_sequences=True)(inputs)
    x = Dropout(0.3)(x)
    x = LSTM(400, return_sequences=True)(x)
    x = Dropout(0.3)(x)
    x = LSTM(400)(x)
    x = Dropout(0.3)(x)
    x = Dense(OUTPUT_LEN, activation='sigmoid')(x)

    model = Model(inputs, x)
    model.compile(loss=multitask_loss, optimizer='rmsprop')
    model.summary()

    print('Training on {} tracks.'.format(len(train_data)))

    if args.usegen:
        history = model.fit_generator(gen, steps_per_epoch=dataset_len / batch_size, epochs=200)
    else:
        history = model.fit(X, y, epochs=200, batch_size=batch_size, verbose=1)
