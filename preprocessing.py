import argparse
import os
import pickle
import json
from multiprocessing import pool
from pygbx.headers import CGameCtnGhost

from pygbx.stadium_blocks import STADIUM_BLOCKS
from pygbx import Gbx, GbxType
from track_utils import create_pattern_data, fit_data_scaler, occupied_track_positions
from block_utils import block_to_tup


# def show_plot(trace):
#     import matplotlib.pyplot as plt
#     from mpl_toolkits.mplot3d import Axes3D
#     fig = plt.figure()
#     ax = fig.add_subplot(111, projection='3d')
#     xs = [p[0] for p in trace]
#     ys = [p[1] for p in trace]
#     zs = [p[2] for p in trace]

#     ax.scatter(xs, ys, zs)
#     plt.show()


def get_at_pos(occ: dict, pos: list) -> tuple:
    '''
    Queries the (block, positions) dict for the target position
    and returns the entry that contains it.

    Args:
        occ (dict): the occupation dictionary
        pos (list): the position to find
    '''
    for block, block_offsets in occ.items():
        for off in block_offsets:
            if off == pos:
                return block, block_offsets
    return None, None


def process_blocks(blocks: list, ghost: CGameCtnGhost, trace_offset: int) -> list:
    '''
    Processes blocks from the Gbx file, given the ghost and the trace offset.

    Traces the path the car took, constructing the "correct"
    sequence of blocks that make out the track. 

    If the car drives on the ground, a special StadiumGrass block is added
    to the sequence.

    Args:
        blocks (list): the list of block tuples to process
        ghost (CGameCtnGhost): the ghost replay to use for tracing
        trace_offset: the offset to use for tracing

    Returns:
        list: blocks ordered by the path the car took in the source replay
    '''
    trace = []
    for idx, record in enumerate(ghost.records):
        for xoff in [0, -trace_offset, trace_offset]:
            for zoff in [0, -trace_offset, trace_offset]:
                for yoff in [0, -trace_offset]:
                    pos = record.get_block_position(xoff, yoff, zoff)

                    if all(tr[1] != pos for tr in trace):
                        time = idx * 100
                        trace.append([time, pos])

    occ = occupied_track_positions(blocks)

    s = []
    queue = blocks[:]
    while len(trace) > 0:
        time, pos = trace[0][0], trace[0][1]

        if time >= ghost.race_time:
            break

        block, offsets = get_at_pos(occ, pos)

        if not block:
            if pos[1] == 1:
                block = (STADIUM_BLOCKS['StadiumGrass'], pos[0], pos[1], pos[2], 0, 0)
                s.append(block)

            trace.pop(0)
            continue

        if offsets:
            trace = [tr for tr in trace if not tr[1] in offsets]

        s.append(block)
        queue.remove(block)
        occ.pop(block)

    return s


def process(replay_gbx: Gbx, trace_offset: int):
    '''
    Processes a single replay using a given trace offset.

    Args:
        replay_gbx (pygbx.Gbx): the Gbx object to process
        trace_offset (int): the trace offset to use for tracing out blocks

    Returns:
        list: the block tuples
    '''
    replays = replay_gbx.get_classes_by_ids([GbxType.REPLAY_RECORD, GbxType.REPLAY_RECORD_OLD])
    ghosts = replay_gbx.get_classes_by_ids([GbxType.GAME_GHOST, GbxType.CTN_GHOST])

    if not ghosts or not replays:
        return None

    ghost = ghosts[0]
    replay = replays[0]

    challenge = replay.track.get_class_by_id(GbxType.CHALLENGE)
    if not challenge:
        return None

    filtered = []
    for block in challenge.blocks:
        t = block_to_tup(block)
        if not t:
            continue

        filtered.append(t)

    return process_blocks(filtered, ghost, trace_offset)


def process_fname(fname: str, trace_offset: int) -> tuple:
    '''
    Processes a single filename given the trace offset
    
    Args:
        fname (str): the filename to the replay file
        trace_offset (int): the trace offset to use for tracing out blocks

    Returns:
        tuple: (filename, block_tuples)
    '''
    print('\tProcessing: \t{}'.format(fname))
    replay_file = Gbx(fname)
    return fname, process(replay_file, trace_offset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
                        help='the folder filename that contains all .Replay.Gbx files')
    parser.add_argument('-o', '--output', required=True,
                        help='the output folder that the preprocessed data is saved to')
    parser.add_argument('-t', '--trace-offset', required=False, type=int, default=1,
                        help='''the offset that will be used for replay tracing - defaults to 1
                        (small = tracing blocks only very near the replay car;
                        large = tracing blocks farther from the car)''')
    parser.add_argument('-l', '--lookback', default=20, type=int,
                        help='the lookback to use in the config file, this setting will not affect the final data')
    args = parser.parse_args()

    try:
        os.makedirs(args.output, exist_ok=True)
    except EnvironmentError:
        pass

    rootdir = os.getcwd()
    traindir = os.path.join(os.getcwd(), args.input)
    os.chdir(traindir)

    train_name = os.path.join(args.output, 'train_data.pkl')
    pattern_name = os.path.join(args.output, 'pattern_data.pkl')
    scaler_name = os.path.join(args.output, 'position_scaler.pkl')
    config_name = os.path.join(args.output, 'config.json')

    trace_offset = args.trace_offset

    train_data = []

    names = os.listdir(traindir)
    names = [name for name in names if name.endswith('.Replay.Gbx')]
    processed = 0
    for i in range(0, len(names), 100):
        end = min(len(names), i + 100)

        p = pool.Pool(initargs=(trace_offset,))
        it = [[name, trace_offset] for name in names[i:end]]
        entries = p.starmap(process_fname, it)
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
        train_file = open(train_name, 'wb+')
        pickle.dump(train_data, train_file)
        train_file.close()
        os.chdir(traindir)

    os.chdir(rootdir)
    train_file = open(train_name, 'wb+')
    pickle.dump(train_data, train_file)
    train_file.close()

    print('-- Creating pattern data...')
    with open(pattern_name, 'wb+') as pattern_file:
        pickle.dump(create_pattern_data(train_data), pattern_file)

    print('-- Scaling position data..')
    with open(scaler_name, 'wb+') as scaler_file:
        pickle.dump(fit_data_scaler(train_data), scaler_file)

    print('-- Saving config file...')
    config = {
        'train_data': 'train_data.pkl',
        'pattern_data': 'pattern_data.pkl',
        'position_scaler': 'position_scaler.pkl',
        'lookback': args.lookback
    }

    with open(config_name, 'w+') as config_file:
        config_file.write(json.dumps(config, indent=4))

