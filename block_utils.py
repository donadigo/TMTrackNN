from pygbx import STADIUM_BLOCKS
from pygbx.headers import MapBlock, Vector3

BID, BX, BY, BZ, BROT, BFLAGS = range(6)
EMPTY_BLOCK = (0, 0, 0, 0, 0)

# TODO: needs a separate dict / list for TM2 Stadium
EDITOR_IDS = {
    1: '1-1-1',
    2: '1-1-2',
    3: '1-1-2',
    4: '1-1-3',
    5: '1-1-3',
    6: '2-1-1',
    7: '2-1-2',
    8: '2-1-3',
    9: '2-1-4',
    10: '2-1-5',
    11: '2-1-6',
    12: '2-1-7',
    13: '2-2-1',
    14: '2-2-2',
    15: '2-2-3',
    16: '2-2-4',
    17: '2-2-5',
    18: '2-2-6',
    19: '2-2-7',
    20: '2-2-8',
    21: '2-3-1',
    22: '2-3-2',
    23: '2-3-3',
    24: '2-3-4',
    25: '2-3-5',
    26: '2-3-6',
    27: '2-3-7',
    28: '2-3-8',
    29: '2-3-9',
    30: '2-4-1',
    31: '2-4-2',
    32: '2-4-3',
    33: '2-4-4',
    34: '2-4-5',
    35: '2-4-6',
    36: '2-4-7',
    37: '2-4-8',
    38: '3-1-1',
    39: '3-1-2',
    40: '3-1-3',
    41: '3-1-4',
    42: '3-1-5',
    43: '3-1-6',
    44: '3-1-7',
    45: '3-2-1',
    46: '3-2-2',
    47: '3-2-3',
    48: '3-2-4',
    49: '3-2-5',
    50: '3-2-6',
    51: '3-3-1',
    52: '3-3-2',
    53: '3-3-3',
    54: '3-3-4',
    55: '3-4-1',
    56: '3-4-2',
    57: '3-4-3',
    58: '3-4-4',
    59: '3-4-5',
    60: '3-4-6',
    61: '3-4-7',
    62: '3-4-8',
    63: '4-1-1',
    64: '4-1-2',
    65: '4-1-3',
    66: '4-1-4',
    67: '4-1-5',
    68: '4-1-6',
    69: '4-1-7',
    70: '4-1-8',
    71: '4-1-9',
    72: '4-2-1',
    73: '4-2-2',
    74: '4-2-3',
    75: '4-2-4',
    76: '4-2-5',
    77: '4-2-6',
    78: '4-3-1',
    79: '4-3-2',
    80: '4-3-3',
    81: '4-3-4',
    82: '4-3-5',
    83: '4-3-6',
    84: '4-3-7',
    85: '4-3-8',
    86: '4-4-1',
    87: '4-4-2',
    88: '4-4-3',
    89: '4-4-4',
    90: '4-4-5',
    91: '4-4-6',
    92: '4-4-7',
    93: '4-4-8',
    94: '4-5-1',
    95: '4-5-2',
    96: '4-5-3',
    97: '4-5-4',
    98: '5-1-1',
    99: '5-1-2',
    100: '5-1-3',
    101: '5-1-4',
    102: '5-1-5',
    103: '5-1-6',
    104: '5-1-7',
    105: '5-2-1',
    106: '5-2-2',
    107: '5-2-3',
    108: '5-2-4',
    109: '5-2-5',
    110: '5-2-6',
    111: '5-2-7',
    112: '5-2-8',
    113: '5-2-9',
    114: '5-3-1',
    115: '5-3-2',
    116: '5-3-3',
    117: '5-3-4',
    118: '5-3-5',
    119: '5-3-6',
    120: '5-3-7',
    121: '5-4-1',
    122: '5-4-2',
    123: '5-4-3',
    124: '5-4-4',
    125: '5-4-5',
    126: '5-4-6',
    127: '5-5-1',
    128: '5-5-2',
    129: '5-5-3',
    130: '5-5-4',
    131: '6-1-1',
    132: '6-1-2',
    133: '6-1-3',
    134: '6-1-4',
    135: '6-1-5',
    136: '6-2-1',
    137: '6-2-2',
    138: '6-2-3',
    139: '6-2-4',
    140: '6-2-5',
    141: '6-2-6',
    142: '6-2-7',
    143: '6-2-8',
    144: '6-2-9',
    145: '6-3-1',
    146: '6-3-2',
    147: '6-3-3',
    148: '6-3-4',
    149: '6-3-5',
    150: '6-3-6',
    151: '6-4-1',
    152: '6-4-2',
    153: '6-4-3',
    154: '6-4-4',
    155: '6-4-5',
    156: '6-4-6',
    157: '6-4-7',
    158: '6-4-8',
    159: '6-5-1',
    160: '6-5-2',
    161: '6-5-3',
    162: '6-5-4',
    163: '6-5-5',
    164: '6-5-6',
    165: '6-5-7',
    166: '6-5-8',
    167: '6-6-1',
    168: '6-6-2',
    169: '6-6-3',
    170: '6-6-4',
    171: '6-6-5',
    172: '6-6-6',
    173: '6-6-7',
    174: '6-6-8',
    175: '6-7-1',
    176: '6-7-2',
    177: '6-7-3',
    178: '6-7-4',
    179: '6-7-5',
    180: '6-7-6',
    181: '6-7-7',
    182: '6-7-8',
    183: '6-8-1',
    184: '6-8-2',
    185: '6-8-3',
    186: '6-8-4',
    187: '6-9-1',
    188: '6-9-2',
    189: '6-9-3',
    190: '6-9-4',
    191: '6-9-5',
    192: '6-9-6',
    193: '6-9-7',
    194: '6-9-8',
    195: '6-9-9',
    196: '7-1-1',
    197: '7-1-2',
    198: '7-1-3',
    199: '7-1-4',
    200: '7-1-5',
    201: '7-1-6',
    202: '7-1-7',
    203: '7-1-8',
    204: '7-1-9',
    205: '7-2-1',
    206: '7-2-2',
    207: '7-2-3',
    208: '7-2-4',
    209: '7-2-5',
    210: '7-3-1',
    211: '7-3-2',
    212: '7-3-3',
    213: '7-3-4',
    214: '7-3-5',
    215: '7-3-6',
    216: '7-4-1',
    217: '7-4-2',
    218: '7-4-3',
    219: '7-4-4',
    220: '7-4-5',
    221: '7-5-1',
    222: '7-5-2',
    223: '7-5-3',
    224: '7-5-4',
    225: '7-5-5',
    226: '7-5-6',
    227: '7-6-1',
    228: '7-6-2',
    229: '7-6-3',
    230: '7-6-4',
    231: '7-6-5',
    232: '7-6-6',
    233: '7-6-7',
    234: '8-1-1',
    235: '8-1-2',
    236: '8-1-3',
    237: '8-1-4',
    238: '8-2-1',
    239: '8-2-2',
    240: '8-2-3',
    241: '8-2-4',
    242: '8-2-5',
    243: '8-2-6',
    244: '8-2-7',
    245: '8-3-1',
    246: '8-3-2',
    247: '8-3-3',
    248: '8-3-4',
    249: '8-3-5',
    250: '8-3-6',
    251: '8-3-7',
    252: '8-3-8',
    253: '8-4-1',
    254: '8-4-2',
    255: '8-4-3',
    256: '8-4-4',
    257: '8-4-5',
    258: '8-4-5',
    259: '8-4-6',
    260: '8-5-1',
    261: '8-5-2',
    262: '8-5-3',
    263: '8-5-4',
    264: '8-6-1',
    265: '8-6-2',
    266: '8-6-3',
    267: '8-6-4',
    268: '8-6-5',
    269: '8-6-6',
    270: '8-6-7',
    271: '8-6-8',
    272: '8-7-1',
    273: '8-7-2',
    274: '8-7-3',
    275: '8-7-4',
    276: '8-7-5',
    277: '8-7-6',
    278: '8-8-1',
    279: '8-8-2',
    280: '8-8-3',
    281: '8-8-4',
    282: '8-8-5',
    283: '8-8-5',
    284: '8-8-6',
    285: '8-8-7',
    286: '8-9-1',
    287: '8-9-2',
    288: '8-9-3',
    289: '8-9-4',
    290: '8-9-5',
    291: '8-9-6',
    292: '8-9-7'
}

BASE_BLOCKS = list(range(6, 98+1)) + \
    list(range(105, 120+1)) + list(range(127, 224+1)) + list(range(227, 233+1))
GROUND_BLOCKS = [20] + list(range(196, 233+1)) + \
    list(range(253, 263+1)) + list(range(272, 277+1)) + \
    list(range(287, 292+1)) + [363]

CONNECT_MAP = {
    6: list(range(6, 93+1)) + [127, 128, 129, 130, 214, 215],
    198: list(range(196, 233+1)),
    264: list(range(264, 269+1)),
    265: list(range(264, 269+1)),
    266: list(range(264, 269+1)),
    270: [270, 271],
    271: [270, 271]
}

DYNAMIC_GROUND_OFFSETS = {
    'StadiumFabricPillarCornerOut': [[0, 0, 0]],
    'StadiumFabricPillarCornerInAir': [[0, 0, 1], [1, 0, 0], [1, 0, 1]],
    'StadiumFabricPillarAir': [[0, 0, 0]]
}

START_LINE_BLOCK = STADIUM_BLOCKS['StadiumRoadMainStartLine']
FINISH_LINE_BLOCK = STADIUM_BLOCKS['StadiumRoadMainFinishLine']

def block_to_tup(block: MapBlock) -> tuple:
    '''
    Converts a MapBlock instance to a tuple.

    Args:
        block (MapBlock): the MapBlock to convert

    Returns:
        tuple: the converted block
    '''
    try:
        return (STADIUM_BLOCKS[block.name], block.position.x, block.position.y, block.position.z, block.rotation, block.flags, block.speed)
    except KeyError:
        return None


def block_from_tup(tup: tuple) -> MapBlock:
    '''
    Converts a tuple to a MapBlock instance.

    Args:
        block (tuple): the tuple to convert

    Returns:
        MapBlock: the converted block
    '''
    block = MapBlock()
    block.name = get_block_name(tup[BID], STADIUM_BLOCKS)
    block.rotation = tup[BROT]
    block.position = Vector3(tup[BX], tup[BY], tup[BZ])
    if len(tup) > 5:
        block.flags = 0x1000 if tup[BFLAGS] == 1 else 0
    return block


def one_hot_bid(block_id: int, num_classes: int) -> list:
    '''
    One hot encodes a block ID.

    Args:
        block_id (int): one based block ID
        num_classes (int): the number of classes

    Returns:
        list: the encoding
    '''
    arr = [0] * num_classes
    if block_id != 0:
        arr[block_id - 1] = 1
    return arr


def one_hot_rotation(rotation: int) -> list:
    '''
    One hot encodes a cardinal rotation.

    Args:
        rotation (int): the cardinal rotation

    Returns:
        list: the encoding
    '''
    arr = [0] * 4
    arr[rotation] = 1
    return arr


def block_to_vec(block: tuple, inp_len: int, num_classes: int, scaler: object, encode_pos=True) -> list:
    '''
    Converts a block tuple to a complete block encoding,
    including its position and rotation.

    Args:
        block (tuple): the block tuple to convert
        inp_len (int): the input length
        num_classes (int): the number of block classes
        scaler (object): the scaler to use to encode position
        encode_pos (bool): whether to encode the position and rotation
    
    Returns:
        list: the encoded block
    '''
    if block[0] == 0:
        return [0] * inp_len

    bid_vec = one_hot_bid(block[BID], num_classes)
    if encode_pos:
        pos_vec = scaler.transform([block[BX:BZ+1]])[0]
        rot_vec = one_hot_rotation(block[BROT])
    else:
        pos_vec = [-1, -1, -1]
        rot_vec = [-1, -1, -1, -1]

    return bid_vec + list(pos_vec) + rot_vec


def pad_block_sequence(seq: list, maxlen: int) -> list:
    '''
    Left pads a block sequence given a max sequence length.

    Args:
        seq (list): the block sequence to pad
        maxlen (int): the maximum length of the resulting sequence

    Returns:
        list: the resulting sequence
    '''
    pad = [EMPTY_BLOCK] * (maxlen - len(seq))
    return pad + seq


def get_block_name(block_id: int, blocks: dict) -> str:
    '''
    Gets the block name by its ID.

    Args:
        block_id (int): the block ID
        blocks (dict): the block mappings
    
    Returns:
        str: the block name
    '''
    for name, _block_id in blocks.items():
        if _block_id == block_id:
            return name
    return None
