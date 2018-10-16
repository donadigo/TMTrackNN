import math
import os
import pickle
import random
import struct
import sys
from os import chdir, getcwd, listdir

import numpy as np

import gbx
import headers
from block_offsets import BLOCK_OFFSETS, rotate_block_offsets, rotate_track, occupied_track_positions
from blocks import (BASE_BLOCKS, BLOCKS, FINISH_LINE_BLOCK, BID, BX, BY, BZ,
                    MULTILAP_LINE_BLOCK, START_LINE_BLOCK, get_block_name,
                    is_checkpoint, is_finish, is_multilap, is_start)
from track_blacklist import BLACKLIST
from multiprocessing import pool
from scipy import spatial

sys.path.append(os.path.realpath('..'))

ENABLE_START_FINISH_GUARD = True
DISCARD_NOISY_TRACKS = True
FILTER_BASE_BLOCKS = True
ENABLE_SMART_SORT = False
MAX_MAP_SIZE = (32, 40, 32)

def filter_base_blocks(blocks):
    l = []
    for block in blocks:
        try:
            if BLOCKS[block.name] in BASE_BLOCKS:
                l.append(block)
        except KeyError:
            continue

    return l

def dist(x,y):
    x = np.array(x)
    y = np.array(y)
    return np.sqrt(np.sum((x-y) ** 2))

def dfs(g, v, end):
    current = v
    explored = [current]
    while len(g) > 1:
        g.remove(current)
        tree = spatial.KDTree(g)
        current = g[tree.query(current)[1]]

        if current[0] > MAX_MAP_SIZE[0] or current[1] > MAX_MAP_SIZE[1] or current[2] > MAX_MAP_SIZE[2]:
            continue

        explored.append(current)

    explored.append(g.pop())
    return explored

def is_noisy(blocks):
    far = 0
    for i in range(1, len(blocks)):
        block_pos = np.array(blocks[i].position)
        prev_pos = np.array(blocks[i - 1].position)

        if dist(block_pos, prev_pos) > 4:
            far += 1

    if far / float(len(blocks)) > 0.2:
        return True

    return False

def sort_blocks(blocks):
    track = [block.to_tup() for block in blocks]
    positions = occupied_track_positions(track)
    positions = [list(pos) for pos in positions]

    v = []
    end = []
    for block in track:
        if block[BID] == START_LINE_BLOCK:
            v = list(block[BX:BZ+1])
        elif block[BID] == FINISH_LINE_BLOCK:
            end = list(block[BX:BZ+1])

    trace = dfs(positions, v, end)
    sorted_track = []
    for pos in trace:
        for block in track:
            if list(block[BX:BZ+1]) == pos:
                sorted_track.append(block)

    return sorted_track

def process_blocks(source_blocks):
    if FILTER_BASE_BLOCKS:
        blocks = filter_base_blocks(source_blocks)
    else:
        blocks = source_blocks[:]

    i = 0

    if DISCARD_NOISY_TRACKS:
        if is_noisy(blocks):
            return None

    if ENABLE_SMART_SORT:
        blocks = sort_blocks(blocks)

        sequences = []
        current_seq = [blocks[0]]
        while i < len(blocks) - 1:
            prev = blocks[i]
            block = blocks[i + 1]

            prev_offsets = occupied_track_positions([prev])
            block_offsets = occupied_track_positions([block])

            m = 100
            for off in block_offsets:
                for off2 in prev_offsets:
                    m = min(m, dist(off, off2))

            if m > 4:
                if len(current_seq) > 5:
                    sequences.append(current_seq)
                current_seq = []
            else:
                current_seq.append(block)

            i += 1
        return sequences
    else:
        return [[block.to_tup() for block in blocks]]

def process(gbx_file, fname):
    challenge = gbx_file.get_class_by_id(gbx.GbxType.CHALLENGE)
    if challenge == None:
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
            if is_start(block.name):
                has_start = True
            elif is_finish(block.name):
                has_finish = True

        except KeyError:
            continue

    if ENABLE_START_FINISH_GUARD and not (has_start and has_finish):
        print('\t-- Skipping map without start and an end\n')
        return None

    sequences = process_blocks(challenge.blocks)
    return (fname, sequences)

rootdir = getcwd()

if len(sys.argv) < 2:
    print('No input folder name specified.')
    sys.exit()

if len(sys.argv) < 3:
    print('No output filename was specified.')
    sys.exit()

traindir = os.path.join(os.getcwd(), sys.argv[1])
chdir(traindir)

def process_fname(fname):
    if fname in BLACKLIST:
        print('\t-- Skipping blacklisted track.\n')
        return None

    print('\tProcessing: \t{}'.format(fname))
    gbx_file = gbx.Gbx(fname)
    return process(gbx_file, fname)


train_data = []

if __name__ == '__main__':
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
        train_file = open(sys.argv[2], 'wb+')
        pickle.dump(train_data, train_file)
        train_file.close()
        chdir(traindir)

    chdir(rootdir)
    train_file = open(sys.argv[2], 'wb+')
    pickle.dump(train_data, train_file)
    train_file.close()