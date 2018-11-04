import argparse
import os
import pickle
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--block-model', required=True,
                    help='the weights filename of the block model')
parser.add_argument('-p', '--pos-model', required=True,
                    help='the weights filename of the position model')
parser.add_argument('-l', '--length', required=True,
                    help='the length in blocks of the track', type=int)
parser.add_argument('-o', '--output', required=True,
                    help='the output filename of the generated track (.Challenge.Gbx)')
parser.add_argument('-t', '--temperature', type=float, default=1.2,
                    help='''sampling temperature, the higher the more "creative" the network is
                    but at the expense of higher chance that the results will be unsatisfying (default is 1.2)''')

args = parser.parse_args()

import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from blocks import BID, BLOCKS, BROT, BX, BY, BZ
from track_utils import fit_position_scaler
from config import NET_CONFIG
from builder import Builder
from savegbx import save_gbx

np.warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


train_data_file = open(NET_CONFIG['train_fname'], 'rb')
train_data = pickle.load(train_data_file)

pattern_data_file = open(NET_CONFIG['patterns_fname'], 'rb')
pattern_data = pickle.load(pattern_data_file)

scaler = fit_position_scaler(train_data)


def progress_callback(completed, total):
    percentage = int(completed / float(total) * 100)
    sys.stdout.write(f'Progress: {percentage}% [{completed} / {total}]\r')
    sys.stdout.flush()


block_model_name = sys.argv[1]
pos_model_name = sys.argv[2]

block_model = load_model(args.block_model)
pos_model = load_model(args.pos_model)

builder = Builder(block_model, pos_model,
                     NET_CONFIG['lookback'], train_data, pattern_data, scaler, temperature=args.temperature)

track = builder.build(args.length, verbose=False, save=False,
                      progress_callback=progress_callback)
print(track)
save_gbx({'track_data': track}, 'data/Template.Challenge.Gbx', args.output)
print(f'Track saved to {args.output}.')
