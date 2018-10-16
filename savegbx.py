import struct
import lzo
import sys
import pickle
from enum import Enum

import gbx
import blocks as bl
from block_offsets import rotate_track

class Action(Enum):
    UNKNOWN = 0
    SAVEBIN = 1
    ROTATE = 2

    @staticmethod
    def from_string(s):
        s = s.lower()
        if s == 'rotate':
            return Action.ROTATE
        elif s == 'savebin':
            return Action.SAVEBIN
        
        return Action.UNKNOWN

CURRENT_VER = 3
BASE_LBS_IDX = 0b1000000000000000000000000000000

GROUND_FLAG = 1 << 12

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


def check_bounds(position):
    return (position[0] >= 0 and position[0] <= 31 and
            position[1] >= 1 and position[1] <= 32 and
            position[2] >= 0 and position[2] <= 31)


def write_block(stored_strings, seen_lookback, block):
    bstr = bytearray()

    bname = bl.get_block_name(block[0])
    bstr += write_lookback_string(stored_strings, seen_lookback, bname)

    bstr += struct.pack('B', block[4])
    bstr += struct.pack('B', max(0, block[1]))
    bstr += struct.pack('B', max(0, block[2]))
    bstr += struct.pack('B', max(0, block[3]))

    flags = 0
    if len(block) > 5:
        flags = block[5]
        if flags & 0x8000:
            flags &= 0x0fff

        if flags & 0x100000:
            flags &= 0x0fffff
            # bstr += write_lookback_string(stored_strings, seen_lookback, 'Nadeo')
            # bstr += struct.pack('i', -1)

    # if block[bl.BY] == 1:
    #     flags |= GROUND_FLAG

    bstr += struct.pack('I', flags)
    return bstr


def rotate_track_challenge(challenge, rotation):
    track = []
    blocks = rotate_track(challenge.blocks[:], rotation)

    for block in blocks:
        bid = bl.BLOCKS[block.name]

        rotation = block.rotation
        position = block.position

        track.append(
            (bid, position[0], position[1], position[2], rotation, block.flags))

    return track


def save_gbx(options, template, output):
    stored_strings = []
    seen_lookback = True

    def data_replace(s, rep, offset, rlen=-1):
        if rlen == -1:
            rlen = len(rep)
        return s[:offset] + rep + s[offset + rlen:]

    temp_gbx = gbx.Gbx(template)
    challenge = temp_gbx.get_class_by_id(gbx.GbxType.CHALLENGE)

    if 'rotation' in options:
        track = rotate_track_challenge(challenge, options['rotation'])
    elif 'input' in options:
        track = pickle.load(open(options['input'], 'rb'))

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

    blocks_chunk_str = bytearray()
    blocks_chunk_str += struct.pack('I', len(track))

    for block in track:
        blocks_chunk_str += write_block(stored_strings, seen_lookback, block)

    udata = data_replace(udata, blocks_chunk_str,
                         temp_gbx.num_blocks_offset, temp_gbx.block_data_size)
    compressed = lzo.compress(bytes(udata), 1, False)

    fs = open(output, 'wb+')

    comp_data_size_offset = temp_gbx.data_size_offset + 4
    comp_data_offset = comp_data_size_offset + 4

    data = data_replace(data, struct.pack('I', len(udata)),
                        temp_gbx.data_size_offset)
    data = data_replace(data, struct.pack(
        'I', len(compressed)), comp_data_size_offset)
    data = data_replace(data, compressed, comp_data_offset)

    fs.write(data)
    fs.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('./{} savebin track-filename.bin template-filename.Challenge.Gbx output-filename.Challenge.Gbx'.format(sys.argv[0]))
        print('./{} rotate [1, 2, 3] template-filename.Challenge.Gbx output-filename.Challenge.Gbx'.format(sys.argv[0]))
        sys.exit()

    options = {}
    action =  Action.from_string(sys.argv[1])
    if action == Action.UNKNOWN:
        print('Unkonwn action \"{}\".'.format(sys.argv[1]))
        sys.exit()
    elif action == Action.ROTATE:
        options['rotation'] = int(sys.argv[2])
    elif action == Action.SAVEBIN:
        options['input'] = sys.argv[2]

    template = sys.argv[3]
    output = sys.argv[4]

    save_gbx(options, template, output)
