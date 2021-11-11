import os
import pickle
import struct
import sys
import lzo
from enum import Enum

from pygbx import Gbx, GbxType, CGameChallenge
from block_utils import BASE_BLOCKS, BID, BROT, BX, BY, BZ, get_block_name
from pygbx.stadium_blocks import STADIUM_BLOCKS
from track_utils import populate_flags, rotate_track


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

class GbxSaveContext(object):
    def __init__(self, seen_lookback: bool):
        self.seen_lookback = seen_lookback
        self.stored_strings = []
        self.data = bytearray()

    def write_lookback_string(self, s: str):
        lbs = bytearray()
        if not self.seen_lookback:
            ver = str(struct.pack('I', CURRENT_VER))
            lbs += ver
            self.seen_lookback = True

        if s not in self.stored_strings:
            idx = struct.pack('I', BASE_LBS_IDX)
            lbs += idx
            lbs += struct.pack('I', len(s))
            lbs += struct.pack(str(len(s)) + 's', bytes(s, 'utf-8'))
            self.stored_strings.append(s)
        else:
            idx = struct.pack('I', BASE_LBS_IDX + self.stored_strings.index(s))
            lbs += idx

        self.data.extend(lbs)

    def write_string(self, s: str):
        self.write_uint32(len(s))
        self.data.extend(struct.pack(str(len(s)) + 's', bytes(s, 'utf-8')))

    def write_byte(self, b: int):
        self.data.extend(struct.pack('B', b))

    def write_uint32(self, i: int):
        self.data.extend(struct.pack('I', i))

    def append_to_string_store(self, s: str):
        if s not in self.stored_strings:
            self.stored_strings.append(s)

    def write_block(self, block: tuple):
        bname = get_block_name(block[BID], STADIUM_BLOCKS)
        self.write_lookback_string(bname)
        self.write_byte(block[BROT])
        self.write_byte(max(0, block[BX]))
        self.write_byte(max(1, block[BY]))
        self.write_byte(max(0, block[BZ]))

        flags = 0
        if len(block) > 5:
            flags = block[5]
            if flags & 0x8000:
                flags &= 0x0fff

            if flags & 0x100000:
                flags &= 0x0fffff

        self.write_uint32(flags)

    def reset(self):
        self.data = bytearray()

CURRENT_VER = 3
BASE_LBS_IDX = 1 << 30
GROUND_FLAG = 1 << 12

MOODS = ['Sunrise', 'Day', 'Sunset', 'Night']
MOOD_WEIGHTS = [0.3, 0.5, 0.1, 0.1]


def rotate_track_challenge(challenge: CGameChallenge, rotation: int) -> list:
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


def get_map_name(output: str) -> str:
    name = os.path.basename(output)
    return name.split('.')[0]


def save_gbx(options: dict, template: str, output: str):
    context = GbxSaveContext(True)

    def data_replace(s, rep, offset, rlen=-1):
        if rlen == -1:
            rlen = len(rep)
        return s[:offset] + rep + s[offset + rlen:]

    temp_gbx = Gbx(template)
    challenge = temp_gbx.get_class_by_id(GbxType.CHALLENGE)
    common = temp_gbx.get_class_by_id(0x03043003)

    if 'rotation' in options:
        track = rotate_track_challenge(challenge, options['rotation'])
    elif 'input' in options:
        track = pickle.load(open(options['input'], 'rb'))
    elif 'track_data' in options:
        track = options['track_data']

    track = populate_flags(track)

    context.append_to_string_store(challenge.map_uid)
    context.append_to_string_store(challenge.environment)
    context.append_to_string_store(challenge.map_author)
    context.append_to_string_store(challenge.map_name)
    context.append_to_string_store(challenge.mood)
    context.append_to_string_store(challenge.env_bg)
    context.append_to_string_store(challenge.env_author)

    udata = bytes(temp_gbx.data)

    temp = open(template, 'rb')
    data = temp.read()

    # We have to be very careful of order we save the data.
    # We begin saving the data from the very end to the beggining of the file,
    # so that all Gbx's class offsets are always valid.

    # Modifying body
    # Blocks
    context.write_uint32(len(track))
    for block in track:
        context.write_block(block)

    info = temp_gbx.positions['block_data']
    if info.valid:
        udata = data_replace(udata, context.data,
                             info.pos, info.size)

    # The mood
    # info = temp_gbx.positions['mood']
    # if info.valid:
    #     mood = random.choices(MOODS, MOOD_WEIGHTS)[0]
    #     print(mood)
    #     udata = data_replace(udata, write_lookback_string(
    #         stored_strings, seen_lookback, mood), info.pos, info.size)

    # Map name in editor
    context.reset()
    if 'map_name' in options:
        map_name = options['map_name']
    else:
        map_name = get_map_name(output)
    
    context.write_string(map_name)

    # The map name
    info = temp_gbx.positions['map_name']
    if info.valid:
        udata = data_replace(udata, context.data, info.pos, info.size)

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
        data = data_replace(data, context.data, info.pos, info.size)

    # New chunk size since track name length could change
    user_data_diff = len(common.track_name) - len(map_name)
    info = temp_gbx.positions['50606083']
    if info.valid:
        prev = temp_gbx.root_parser.pos
        temp_gbx.root_parser.pos = info.pos
        new_chunk_size = temp_gbx.root_parser.read_uint32() - user_data_diff
        temp_gbx.root_parser.pos = prev

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
