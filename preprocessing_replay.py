import pickle

# import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from block_offsets import BLOCK_OFFSETS
from blocks import BID, BROT, BX, BY, BZ
from gbx import Gbx, GbxType
from track_utils import get_block_name, rotate_block_offsets, occupied_track_positions
import argparse
import os
from multiprocessing import pool

BLOCK_SIZE_XZ = 32
BLOCK_SIZE_Y = 8


# def show_plot(trace):
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     xs = [p[0] for p in trace]
#     ys = [p[1] for p in trace]
#     zs = [p[2] for p in trace]

#     ax.scatter(xs, ys, zs)
#     plt.show()


def get_at_pos(occ, pos):
    for block, block_offsets in occ.items():
        for off in block_offsets:
            if off == pos:
                return block
    return None


def process_blocks(blocks, ghost):
    trace = []
    for record in ghost.records:
        for xoff in [0, -1, 1]:
            for zoff in [0, -1, 1]:
                x = int((record.position[0] + xoff) / BLOCK_SIZE_XZ)
                y = int((record.position[1]) / BLOCK_SIZE_Y)
                z = int((record.position[2] + zoff) / BLOCK_SIZE_XZ)
                pos = [x, y, z]
                if not pos in trace:
                    trace.append(pos)

    occ = occupied_track_positions(blocks)

    s = []
    queue = blocks[:]
    for pos in trace:
        if len(queue) == 0:
            break

        block = get_at_pos(occ, pos)

        if not block:
            block = get_at_pos(occ, [pos[0], pos[1] - 1, pos[2]])

        if not block:
            continue

        s.append(block)
        queue.remove(block)
        occ.pop(block)

    return s


def process(replay_gbx):
    replays = replay_gbx.get_classes_by_ids(
        [GbxType.REPLAY_RECORD, GbxType.REPLAY_RECORD_TM2])
    ghosts = replay_gbx.get_classes_by_ids(
        [GbxType.GAME_GHOST, GbxType.CTN_GHOST])

    if len(ghosts) == 0 or len(replays) == 0:
        return None

    ghost = ghosts[0]
    replay = replays[0]

    challenge = replay.track.get_class_by_id(GbxType.CHALLENGE)
    if not challenge:
        return None

    filtered = []
    for block in challenge.blocks:
        t = block.to_tup()
        if not t:
            continue

        filtered.append(t)

    return process_blocks(filtered, ghost)


def process_fname(fname):
    print('\tProcessing: \t{}'.format(fname))
    replay_file = Gbx(fname)
    return fname, process(replay_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='the folder filename that contains all .Replay.Gbx files')
    parser.add_argument('-o', '--output', required=True,
                        help='the output filename that the preprocessed data is saved to')
    args = parser.parse_args()

    rootdir = os.getcwd()
    traindir = os.path.join(os.getcwd(), args.input)
    os.chdir(traindir)

    train_data = []

    names = os.listdir(traindir)
    processed = 0
    for i in range(0, len(names), 100):
        p = pool.Pool()
        end = min(len(names), i + 100)
        entries = p.map(process_fname, names[i:end])
        p.close()

        for entry in entries:
            fname = entry[0]
            blocks = entry[1]
            if not blocks:
                continue

            train_data.append((fname, blocks))
            processed += 1
        print(f'-- Processed {processed} tracks.')
        print(f'-- Saving training data, length: {len(train_data)}')
        os.chdir(rootdir)
        train_file = open(args.output, 'wb+')
        pickle.dump(train_data, train_file)
        train_file.close()
        os.chdir(traindir)

    os.chdir(rootdir)
    train_file = open(args.output, 'wb+')
    pickle.dump(train_data, train_file)
    train_file.close()
