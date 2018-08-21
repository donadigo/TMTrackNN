from __future__ import print_function
import numpy as np
import random
import struct
import headers
import sys
import pickle

from os import listdir, chdir, getcwd
import math
import sys
import os

import gbx
from blocks import BLOCKS, BASE_BLOCKS, START_LINE_BLOCK, FINISH_LINE_BLOCK, MULTILAP_LINE_BLOCK, is_start, is_finish, is_multilap, is_checkpoint
from track_blacklist import BLACKLIST

sys.path.append(os.path.realpath('..'))

ENABLE_START_FINISH_GUARD = False
ENABLE_FINISH_CLEANUP = True
FILTER_BASE_BLOCKS = True
MAX_MAP_SIZE = (32, 40, 32)
# ENABLE_SMART_SORT = False

# def block_distance(block_a, block_b):
#     return math.sqrt(sum((x - y) ** 2 for x, y in zip(block_a.position, block_b.position)))


# def find_closest_block_dist(blocks, target):
#     closest = None
#     score = sys.maxint
#     for block in blocks:
#         if block == target:
#             continue

#         new_score = block_distance(target, block)
#         if new_score < score:
#             closest = block
#             score = new_score

#     return closest, score


# def euclidean_sort(blocks):
#     search_blocks = blocks
#     s = []

#     current_block = None
#     for block in blocks:
#         try:
#             if BLOCKS[block.name] == START_LINE_BLOCK or BLOCKS[block.name] == MULTILAP_LINE_BLOCK:
#                 current_block = block
#                 break
#         except KeyError:
#             continue

#     if current_block == None:
#         return blocks

#     search_blocks.remove(current_block)
#     # s.append([])
#     s.append(current_block)

#     while len(search_blocks) > 0:
#         current_block, score = find_closest_block_dist(
#             search_blocks, current_block)
#         # if score > MAX_BLOCK_DISTANCE:
#         #     print(
#         #         '\t-- Closest block distance is too big, creating a new block sequence.')
#         #     s.append([])

#         s.append(current_block)
#         search_blocks.remove(current_block)

#     return s


def finish_cleanup_blocks(blocks):
    # Find last finish in the sequence
    idx = -1
    for i, block in enumerate(reversed(blocks)):
        if BLOCKS[block.name] == FINISH_LINE_BLOCK:
            idx = len(blocks) - i - 1
            break

        # Appears that we have checkpoints after the finish was placed,
        # return the original list
        if idx == -1 and is_checkpoint(block.name):
            return blocks

    if idx == -1:
        return blocks

    return blocks[:idx + 1]


def filter_base_blocks(blocks):
    l = []
    for block in blocks:
        try:
            if BLOCKS[block.name] in BASE_BLOCKS:
                l.append(block)
        except KeyError:
            continue

    return l


def process_blocks(source_blocks):
    if FILTER_BASE_BLOCKS:
        blocks = filter_base_blocks(source_blocks)
    else:
        blocks = source_blocks[:]

    if ENABLE_FINISH_CLEANUP:
        blocks = finish_cleanup_blocks(blocks)

    # if ENABLE_SMART_SORT:
    #     return euclidean_sort(blocks)

    return blocks

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
    has_multilap = False
    for block in challenge.blocks:
        try:
            if is_start(block.name):
                has_start = True
            elif is_finish(block.name):
                has_finish = True
            elif is_multilap(block.name):
                has_multilap = True

        except KeyError:
            continue

    if ENABLE_START_FINISH_GUARD and not ((has_start and has_finish) or has_multilap):
        print('\t-- Skipping map without start and an end\n')
        return None

    sequence = process_blocks(challenge.blocks)
    blocks = [block.to_tup() for block in sequence]

    return (fname, blocks)


def save_generic_data(data):
    f = open('data.txt', 'w+')
    for seq in data:
        line = ''
        for i, block in enumerate(seq):
            fs = '{} {} {} {} {}'
            if i < len(seq) - 1:
                fs += ','

            line += fs.format(
                block[0], block[1], block[2], block[3], block[4])
        f.write(line + '\n')

    f.close()

rootdir = getcwd()

if len(sys.argv) < 2:
    print('No input folder name specified.')
    sys.exit()

if len(sys.argv) < 3:
    print('No output filename was specified.')
    sys.exit()

traindir = os.path.join(os.getcwd(), sys.argv[1])
chdir(traindir)

train_data = []

print('-- Processing train data')
i = 1
for fname in listdir(traindir):
    print('\tProcessing {}:\t{}'.format(i, fname))
    i += 1

    if fname in BLACKLIST:
        print('\t-- Skipping blacklisted track.\n')
        continue

    gbx_file = gbx.Gbx(fname)
    entry = process(gbx_file, fname)
    if entry == None:
        continue

    train_data.append(entry)

print('Saving training data, length: {}'.format(len(train_data)))
chdir(rootdir)
train_file = open(sys.argv[2], 'w+')
pickle.dump(train_data, train_file)
train_file.close()