import os
import pickle
import random
import struct
import sys
import lzo
from enum import Enum

import core.gbx as gbx
from core.block_utils import BID, BROT, BX, BY, BZ, get_block_name
from core.stadium_blocks import STADIUM_BLOCKS, BASE_BLOCKS
from core.track_utils import populate_flags, rotate_track


class Action(Enum):
    UNKNOWN = 0
    SAVEBIN = 1
    TRACK_DATA = 2
    ROTATE = 3

    @staticmethod
    def from_string(s):
        s = s.lower()
        if s == 'rotate':
            return Action.ROTATE
        elif s == 'savebin':
            return Action.SAVEBIN
        elif s == 'trackdata':
            return Action.TRACK_DATA

        return Action.UNKNOWN


CURRENT_VER = 3
BASE_LBS_IDX = 1 << 30
GROUND_FLAG = 1 << 12

MOODS = ['Sunrise', 'Day', 'Sunset', 'Night']
MOOD_WEIGHTS = [0.3, 0.5, 0.1, 0.1]


def append_to_store(stored_strings, s):
    if s not in stored_strings:
        stored_strings.append(s)


def write_lookback_string(stored_strings, seen_lookback, s):
    lbs = bytearray()
    if not seen_lookback:
        ver = str(struct.pack('I', CURRENT_VER))
        lbs += ver
        seen_lookback = True

    if s not in stored_strings:
        idx = struct.pack('I', BASE_LBS_IDX)
        lbs += idx
        lbs += struct.pack('I', len(s))
        lbs += struct.pack(str(len(s)) + 's', bytes(s, 'utf-8'))
        stored_strings.append(s)
    else:
        idx = struct.pack('I', BASE_LBS_IDX + stored_strings.index(s))
        lbs += idx

    return lbs

def write_block(stored_strings, seen_lookback, block):
    bstr = bytearray()

    bname = get_block_name(block[BID], STADIUM_BLOCKS)
    bstr += write_lookback_string(stored_strings, seen_lookback, bname)

    bstr += struct.pack('B', block[BROT])
    bstr += struct.pack('B', max(0, block[BX]))
    bstr += struct.pack('B', max(1, block[BY]))
    bstr += struct.pack('B', max(0, block[BZ]))

    flags = 0
    if len(block) > 5:
        flags = block[5]
        if flags & 0x8000:
            flags &= 0x0fff

        if flags & 0x100000:
            flags &= 0x0fffff

    bstr += struct.pack('I', flags)
    return bstr


def rotate_track_challenge(challenge, rotation):
    track = []
    blocks = rotate_track(challenge.blocks[:], rotation)

    for block in blocks:
        bid = STADIUM_BLOCKS[block.name]

        rotation = block.rotation
        position = block.position

        if not bid in BASE_BLOCKS:
            continue
        track.append((bid, position.x, position.y, position.z, rotation, block.flags))

    return track


def get_map_name(output):
    name = os.path.basename(output)
    return name.split('.')[0]


def save_gbx(options, template, output):
    stored_strings = []
    seen_lookback = True

    def data_replace(s, rep, offset, rlen=-1):
        if rlen == -1:
            rlen = len(rep)
        return s[:offset] + rep + s[offset + rlen:]

    temp_gbx = gbx.Gbx(template)
    challenge = temp_gbx.get_class_by_id(gbx.GbxType.CHALLENGE)
    common = temp_gbx.get_class_by_id(0x03043003)

    if 'rotation' in options:
        track = rotate_track_challenge(challenge, options['rotation'])
    elif 'input' in options:
        track = pickle.load(open(options['input'], 'rb'))
    elif 'track_data' in options:
        track = options['track_data']

    track = populate_flags(track)

    append_to_store(stored_strings, challenge.map_uid)
    append_to_store(stored_strings, challenge.environment)
    append_to_store(stored_strings, challenge.map_author)
    append_to_store(stored_strings, challenge.map_name)
    append_to_store(stored_strings, challenge.mood)
    append_to_store(stored_strings, challenge.env_bg)
    append_to_store(stored_strings, challenge.env_author)

    udata = bytes(temp_gbx.data)

    temp = open(template, 'rb')
    data = temp.read()

    # We have to be very careful of order we save the data.
    # We begin saving the data from the very end to the beggining of the file,
    # so that all Gbx's class offsets are always valid.

    # Modifying body
    # Blocks
    blocks_chunk_str = bytearray()
    blocks_chunk_str += struct.pack('I', len(track))
    for block in track:
        blocks_chunk_str += write_block(stored_strings, seen_lookback, block)

    info = temp_gbx.positions['block_data']
    if info.valid:
        udata = data_replace(udata, blocks_chunk_str,
                             info.pos, info.size)

    # The mood
    # info = temp_gbx.positions['mood']
    # if info.valid:
    #     mood = random.choices(MOODS, MOOD_WEIGHTS)[0]
    #     print(mood)
    #     udata = data_replace(udata, write_lookback_string(
    #         stored_strings, seen_lookback, mood), info.pos, info.size)

    # Map name in editor
    if 'map_name' in options:
        map_name = options['map_name']
    else:
        map_name = get_map_name(output)
    map_name_str = bytearray()
    map_name_str += struct.pack('I', len(map_name))
    map_name_str += struct.pack(str(len(map_name)) +
                                's', bytes(map_name, 'utf-8'))

    # The map name
    info = temp_gbx.positions['map_name']
    if info.valid:
        udata = data_replace(udata, map_name_str, info.pos, info.size)

    compressed = lzo.compress(bytes(udata), 1, False)

    fs = open(output, 'wb+')

    # New data and compressed data size
    data_size_offset = temp_gbx.positions['data_size'].pos

    comp_data_size_offset = data_size_offset + 4
    comp_data_offset = comp_data_size_offset + 4

    data = data_replace(data, struct.pack('I', len(udata)),
                        data_size_offset)
    data = data_replace(data, struct.pack(
        'I', len(compressed)), comp_data_size_offset)
    data = data_replace(data, compressed, comp_data_offset)

    # Modifying header
    # The track name in map chooser
    info = temp_gbx.positions['track_name']
    if info.valid:
        data = data_replace(data, map_name_str, info.pos, info.size)

    # New chunk size since track name length could change
    user_data_diff = len(common.track_name) - len(map_name)
    info = temp_gbx.positions['50606083']
    if info.valid:
        new_chunk_size = temp_gbx.root_parser.read_info(
            info, temp_gbx.root_parser.read_uint32) - user_data_diff
        data = data_replace(data, struct.pack(
            'I', new_chunk_size), info.pos, info.size)

    # Finally, the user data size
    new_user_data_size = temp_gbx.user_data_size - user_data_diff
    info = temp_gbx.positions['user_data_size']
    if info.valid:
        data = data_replace(data, struct.pack(
            'I', new_user_data_size), info.pos, info.size)

    fs.write(data)
    fs.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('./{} savebin track-filename.bin template-filename.Challenge.Gbx output-filename.Challenge.Gbx'.format(sys.argv[0]))
        print('./{} rotate [1, 2, 3] template-filename.Challenge.Gbx output-filename.Challenge.Gbx'.format(sys.argv[0]))
        sys.exit()

    options = {}
    action = Action.from_string(sys.argv[1])
    if action == Action.UNKNOWN:
        print('Unkonwn action \"{}\".'.format(sys.argv[1]))
        sys.exit()
    elif action == Action.ROTATE:
        options['rotation'] = int(sys.argv[2])
    elif action == Action.TRACK_DATA:
        options['track_data'] = eval(sys.argv[2])
    elif action == Action.SAVEBIN:
        options['input'] = sys.argv[2]

    template = sys.argv[3]
    output = sys.argv[4]

    save_gbx(options, template, output)
