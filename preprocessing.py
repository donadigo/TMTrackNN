import argparse
import math
import os
import pickle
import random
import struct
from multiprocessing import pool
from os import chdir, getcwd, listdir

import numpy as np

import gbx
import headers
from block_offsets import BLOCK_OFFSETS
import blocks as bl
from track_blacklist import BLACKLIST
from track_utils import track_sort, dist

ENABLE_START_FINISH_GUARD = True
FILTER_BASE_BLOCKS = True
ENABLE_SMART_SORT = True
MAX_MAP_SIZE = (32, 40, 32)


def filter_base_blocks(blocks):
    l = []
    for block in blocks:
        try:
            if bl.BLOCKS[block.name] in bl.BASE_BLOCKS:
                l.append(block)
        except KeyError:
            continue

    return l


def sort_blocks(blocks):
    track = [block.to_tup() for block in blocks]

    i = 0
    while i < len(track):
        block = track[i]
        if block[1] > 31 or block[2] > 32 or block[3] > 31:
            track.remove(block)
        else:
            i += 1

    return track_sort(track)


def process_blocks(source_blocks):
    if FILTER_BASE_BLOCKS:
        blocks = filter_base_blocks(source_blocks)
    else:
        blocks = source_blocks[:]

    if ENABLE_SMART_SORT:
        blocks = sort_blocks(blocks)
        return [blocks]
    else:
        return [[block.to_tup() for block in blocks]]


def process(gbx_file, fname):
    challenge = gbx_file.get_class_by_id(gbx.GbxType.CHALLENGE)
    if challenge is None:
        print('\t--This file is corrupted or is not a challenge')
        return None

    map_size = challenge.map_size
    if map_size[0] > MAX_MAP_SIZE[0] or map_size[1] > MAX_MAP_SIZE[1] or map_size[2] > MAX_MAP_SIZE[2]:
        print('\t-- Skipping, there is not yet support for bigger maps than 32x32x32\n')
        return None

    has_start = False
    has_finish = False
    for block in challenge.blocks:
        try:
            if bl.is_start(block.name):
                has_start = True
            elif bl.is_finish(block.name):
                has_finish = True

        except KeyError:
            continue

    if ENABLE_START_FINISH_GUARD and not (has_start and has_finish):
        print('\t-- Skipping map without start and an end\n')
        return None

    sequences = process_blocks(challenge.blocks)
    return (fname, sequences)


def process_fname(fname):
    if fname in BLACKLIST:
        print('\t-- Skipping blacklisted track.\n')
        return None

    print('\tProcessing: \t{}'.format(fname))
    gbx_file = gbx.Gbx(fname)
    return process(gbx_file, fname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='the folder filename that contains all .Challenge.Gbx files')
    parser.add_argument('-o', '--output', required=True,
                        help='the output filename that the preprocessed data is saved to')
    args = parser.parse_args()

    rootdir = getcwd()
    traindir = os.path.join(os.getcwd(), args.input)
    chdir(traindir)

    train_data = []

    names = listdir(traindir)
    for i in range(0, len(names), 100):
        p = pool.Pool()
        end = min(len(names) - 1, i + 100)
        entries = p.map(process_fname, names[i:end])
        p.close()

        for entry in entries:
            if not entry:
                continue

            fname = entry[0]
            sequences = entry[1]
            for seq in sequences:
                train_data.append((fname, seq))
        print(f'-- Processed {i + 100} tracks.')
        print(f'-- Saving training data, length: {len(train_data)}')
        chdir(rootdir)
        train_file = open(args.output, 'wb+')
        pickle.dump(train_data, train_file)
        train_file.close()
        chdir(traindir)

    chdir(rootdir)
    train_file = open(args.output, 'wb+')
    pickle.dump(train_data, train_file)
    train_file.close()
