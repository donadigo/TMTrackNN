import numpy as np
from pygbx.stadium_blocks import STADIUM_BLOCKS
from block_utils import DYNAMIC_GROUND_OFFSETS, CONNECT_MAP, BID, BROT, BX, BY, BZ, BFLAGS, block_from_tup, get_block_name, block_to_tup
from pygbx.headers import Vector3
from pygbx.stadium_block_offsets import STADIUM_BLOCK_OFFSETS
from sklearn.preprocessing import MinMaxScaler


def rotate(vec, rot):
    if rot == 1:
        r = np.array([[0, 1], [-1, 0]])
    elif rot == 2:
        r = np.array([[-1, 0], [0, -1]])
    elif rot == 3:
        r = np.array([[0, -1], [1, 0]])
    else:
        return vec

    t = np.array([vec[0], vec[2]])
    x, z = np.dot(t, r)
    return [x, vec[1], z]


def rotate_track(blocks, rotation):
    for block in blocks:
        rotated, _, _ = rotate_block_offsets(
            [block.position, [0, 0, 0], [31, 0, 31]], rotation)
        rotated = rotated[0]

        try:
            offsets = STADIUM_BLOCK_OFFSETS[block.name]
            offsets, _, _ = rotate_block_offsets(offsets, block.rotation)
            _, xoff, zoff = rotate_block_offsets(offsets, rotation)
            block.position = Vector3(rotated[0] + xoff, rotated[1], rotated[2] + zoff)
        except KeyError:
            block.position = Vector3(rotated[0], rotated[1], rotated[2])

        block.rotation = (block.rotation + rotation) % 4

    return blocks


def rotate_track_tuples(tblocks, rotation):
    blocks = []
    for tup in tblocks:
        block = block_from_tup(tup)
        blocks.append(block)

    return [block_to_tup(block) for block in rotate_track(blocks, rotation)]


def get_cardinal_position(pos, rotation):
    if rotation == 0:
        return [pos[0], pos[1], pos[2] + 1]
    elif rotation == 1:
        return [pos[0] - 1, pos[1], pos[2]]
    elif rotation == 2:
        return [pos[0], pos[1], pos[2] - 1]
    elif rotation == 3:
        return [pos[0] + 1, pos[1], pos[2]]

    return pos


def populate_flags(track, use_list=True):
    populated = []
    for i, block in enumerate(track):
        occ = {}
        if i > 0:
            occ.update(occupied_track_positions([track[i - 1]]))
        if i < len(track) - 1:
            occ.update(occupied_track_positions([track[i + 1]]))

        flags = 0
        if is_on_ground(block):
            flags |= 0x1000

        if block[BID] in CONNECT_MAP:
            connections = set()
            candidates = CONNECT_MAP[block[BID]]
            for rotation in range(4):
                pos = get_cardinal_position(list(block[BX:BZ+1]), rotation)

                for neighbour, offsets in occ.items():
                    if pos in offsets and neighbour[BID] in candidates:
                        connections.add(rotation)

            cnum = len(connections)
            if cnum == 0:
                flags &= ~0x7
            elif cnum == 1:
                flags |= 0x1
            elif cnum == 2:
                if (0 in connections and 2 in connections) or (1 in connections and 3 in connections):
                    flags |= 0x3
                else:
                    flags |= 0x2
            elif cnum == 3:
                flags |= 0x4
            elif cnum == 4:
                flags |= 0x5

        populated.append(
            (block[BID], block[BX], block[BY], block[BZ], block[BROT], flags))
    return populated


def is_on_ground(block):
    try:
        offsets = STADIUM_BLOCK_OFFSETS[get_block_name(block[BID], STADIUM_BLOCKS)]
        for offset in offsets:
            if block[BY] + offset[1] == 1:
                return True
    except KeyError:
        pass

    return False


def rotate_block_offsets(offsets, rot):
    rotated = [rotate(off, rot) for off in offsets]
    max_x, max_z = 0, 0

    def get_x(vec): return abs(vec[0])

    def get_z(vec): return abs(vec[2])

    if rot == 1:
        max_x = max(rotated, key=get_x)[0]
    elif rot == 2:
        max_x = max(rotated, key=get_x)[0]
        max_z = max(rotated, key=get_z)[2]
    elif rot == 3:
        max_z = max(rotated, key=get_z)[2]
    else:
        return rotated, 0, 0

    return [[off[0] + abs(max_x), off[1], off[2] + abs(max_z)] for off in rotated], max_x, max_z


def occupied_track_positions(track):
    positions = {}
    for block in track:
        name = get_block_name(block[BID], STADIUM_BLOCKS)
        if not name:
            continue

        try:
            if is_on_ground(block) and name in DYNAMIC_GROUND_OFFSETS:
                offsets = DYNAMIC_GROUND_OFFSETS[name]
            else:
                offsets = STADIUM_BLOCK_OFFSETS[name]
        except KeyError:
            continue

        offsets, _, _ = rotate_block_offsets(offsets, block[BROT])
        block_positions = []
        for offset in offsets:
            block_positions.append(Vector3(
                block[BX] + offset[0],
                block[BY] + offset[1],
                block[BZ] + offset[2]
            ))

        positions[block] = block_positions

    return positions


def occupied_track_vectors(track):
    occ = occupied_track_positions(track)
    vectors = []
    for p in list(occ.values()):
        vectors.extend(p)

    return vectors


def intersects(track, block):
    track_offsets = occupied_track_vectors(track)
    block_offsets = occupied_track_vectors([block])

    for block_off in block_offsets:
        for track_off in track_offsets:
            if block_off == track_off:
                return True
    return False


def dist(x, y):
    x = np.array(x)
    y = np.array(y)
    return np.sqrt(np.sum((x-y) ** 2))


def fit_data_scaler(train_data):
    scaler = MinMaxScaler()
    X = []

    for entry in train_data:
        v = vectorize_track(entry[1])
        for block in v:
            X.append(block[BX:BZ+1])

    scaler.fit(X)
    return scaler


def vectorize_track(track):
    v = track[:]
    X = []
    for i in range(len(track) - 1, -1, -1):
        current = track[i]
        prev = track[i - 1]

        X.append([
            current[BX] - prev[BX],
            current[BY] - prev[BY],
            current[BZ] - prev[BZ]
        ])

        v[i] = (current[BID], X[-1][0],
                X[-1][1], X[-1][2], current[BROT], current[BFLAGS])

    block = track[0]
    v[0] = (block[BID], 0, 0, 0, block[BROT], block[BFLAGS])
    return v


def create_pattern_data(train_data):
    patterns = {}
    for entry in train_data:
        track = entry[1]
        for i in range(1, len(track) - 1):
            prev = track[i - 1]
            n = track[i]

            rotated = rotate_track_tuples([prev, n], (4 - prev[BROT]) % 4)

            prev = rotated[0]
            n = rotated[1]
            n = (n[BID], n[BX] - prev[BX], n[BY] -
                 prev[BY], n[BZ] - prev[BZ], n[BROT])

            prev = prev[BID]

            if not (prev, n) in patterns:
                patterns[(prev, n)] = 1
            else:
                patterns[(prev, n)] += 1

    return patterns
