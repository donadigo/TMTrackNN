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
parser.add_argument('-c', '--config', required=True,
                    help='the config JSON file to use for building')

args = parser.parse_args()

import numpy as np
from keras.models import load_model
from pygbx.stadium_blocks import STADIUM_BLOCKS

from config import load_config
from builder import Builder
from savegbx import save_gbx

np.warnings.filterwarnings('ignore')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

POS_LEN = 3
ROTATE_LEN = 4

INP_LEN = len(STADIUM_BLOCKS) + POS_LEN + ROTATE_LEN

config = load_config(args.config)

pattern_data_file = open(config['pattern_data'], 'rb')
pattern_data = pickle.load(pattern_data_file)

scaler_file = open(config['position_scaler'], 'rb')
scaler = pickle.load(scaler_file)


def progress_callback(completed: int, total: int):
    percentage = int(completed / float(total) * 100)
    sys.stdout.write(f'Progress: {percentage}% [{completed} / {total}]\r')
    sys.stdout.flush()

block_model = load_model(args.block_model)
pos_model = load_model(args.pos_model)
builder = Builder(block_model, pos_model,
                  config['lookback'], None, pattern_data, scaler, temperature=args.temperature)

track = builder.build(args.length, verbose=False, progress_callback=progress_callback, map_size=(32, 32, 32))
print(track)
save_gbx({'track_data': track}, 'data/Template.Challenge.Gbx', args.output)
print(f'Track saved to {args.output}.')
