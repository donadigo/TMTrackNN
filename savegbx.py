import struct
import lzo
import sys
import pickle

import gbx
import blocks as bl

TEMPLATE_FNAME = 'data/Template.Challenge.Gbx'

# Uncompressed data info
BLCK_NUM_OFFSET = 0x13B
BLCK_DATA_SZ = 0x19C - BLCK_NUM_OFFSET

# Template file offsets
DATA_SZ_OFFSET = 0x121B
COMP_DATA_SZ_OFFSET = DATA_SZ_OFFSET + 4
COMP_DATA_OFFSET = COMP_DATA_SZ_OFFSET + 4

CURRENT_VER = 3
BASE_LBS_IDX = 0b1000000000000000000000000000000

GROUND_FLAG = 1 << 12

if len(sys.argv) < 2:
    print('No input track filenname specified.')
    sys.exit()

if len(sys.argv) < 3:
    print('No output GBX filename was specified.')
    sys.exit()

stored_strings = []
seen_lookback = True
track = pickle.load(open(sys.argv[1], 'rb'))

saved_fname = sys.argv[2]

def str_replace(s, rep, offset, rlen=-1):
    if rlen == -1:
        rlen = len(rep)
    return s[:offset] + rep + s[offset + rlen:]


def write_lookback_string(s):
    global seen_lookback
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

def write_block(block):
    bstr = bytearray()

    bname = bl.get_block_name(block[0])
    bstr += write_lookback_string(bname)

    bstr += struct.pack('B', block[4])
    bstr += struct.pack('B', block[1])
    bstr += struct.pack('B', block[2])
    bstr += struct.pack('B', block[3])

    flags = 0
    if block[bl.BY] == 1:
        flags |= GROUND_FLAG
        
    bstr += struct.pack('I', flags)
    return bstr

def append_to_store(s):
    if s not in stored_strings:
        stored_strings.append(s)


temp_gbx = gbx.Gbx(TEMPLATE_FNAME)
challenge = temp_gbx.get_class_by_id(gbx.GbxType.CHALLENGE)
append_to_store(challenge.map_uid)
append_to_store(challenge.environment)
append_to_store(challenge.map_author)
append_to_store(challenge.map_name)
append_to_store(challenge.mood)
append_to_store(challenge.env_bg)
append_to_store(challenge.env_author)

udata = bytes(temp_gbx.data)

temp = open(TEMPLATE_FNAME, 'rb')
data = temp.read()

blocks_chunk_str = bytearray()
blocks_chunk_str += struct.pack('I', len(track))

for block in track:
    blocks_chunk_str += write_block(block)

udata = str_replace(udata, blocks_chunk_str, BLCK_NUM_OFFSET, BLCK_DATA_SZ)
compressed = lzo.compress(bytes(udata), 1, False)

fs = open(saved_fname, 'wb+')

data = str_replace(data, struct.pack('I', len(udata)), DATA_SZ_OFFSET)
data = str_replace(data, struct.pack(
    'I', len(compressed)), COMP_DATA_SZ_OFFSET)
data = str_replace(data, compressed, COMP_DATA_OFFSET)

fs.write(data)
fs.close()
