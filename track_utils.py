import numpy as np
from blocks import BID, BROT, BX, BY, BZ, get_block_name, is_start
from headers import MapBlock
from block_offsets import BLOCK_OFFSETS
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
            offsets = BLOCK_OFFSETS[block.name]
            offsets, _, _ = rotate_block_offsets(offsets, block.rotation)
            _, xoff, zoff = rotate_block_offsets(offsets, rotation)
            block.position = (rotated[0] + xoff, rotated[1], rotated[2] + zoff)
        except KeyError:
            block.position = rotated

        block.rotation = (block.rotation + rotation) % 4

    return blocks


def rotate_track_tuples(tblocks, rotation):
    blocks = []
    for tup in tblocks:
        block = MapBlock()
        block.name = get_block_name(tup[BID])
        block.rotation = tup[BROT]
        block.position = [tup[BX], tup[BY], tup[BZ]]
        blocks.append(block)

    return [block.to_tup() for block in rotate_track(blocks, rotation)]


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


def populate_flags(track):
    populated = []
    for i, block in enumerate(track):
        occ = []
        if i > 0:
            occ.extend(occupied_track_positions([track[i - 1]]))
        if i < len(track) - 1:
            occ.extend(occupied_track_positions([track[i + 1]]))

        flags = 0
        if is_on_ground(block):
            flags |= 0x1000

        # is road
        if block[BID] == 6:
            connections = []
            for rotation in range(4):
                pos = get_cardinal_position(list(block[BX:BZ+1]), rotation)
                if pos in occ:
                    connections.append(rotation)

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
        offsets = BLOCK_OFFSETS[get_block_name(block[BID])]
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
    positions = []
    for block in track:
        name = get_block_name(block[BID])
        if not name:
            continue

        try:
            offsets = BLOCK_OFFSETS[name]
        except KeyError:
            continue

        offsets, _, _ = rotate_block_offsets(offsets, block[BROT])
        for offset in offsets:
            positions.append([
                block[BX] + offset[0],
                block[BY] + offset[1],
                block[BZ] + offset[2]
            ])

    return positions


def intersects(track, block):
    track_offsets = occupied_track_positions(track)
    block_offsets = occupied_track_positions([block])

    for block_off in block_offsets:
        for track_off in track_offsets:
            if block_off == track_off:
                return True
    return False


def dist(x, y):
    x = np.array(x)
    y = np.array(y)
    return np.sqrt(np.sum((x-y) ** 2))


def track_sort(track):
    def occupied(track):
        positions = []
        for block in track:
            name = get_block_name(block[BID])
            if not name:
                continue

            try:
                offsets = BLOCK_OFFSETS[name]
            except KeyError:
                continue

            offsets, _, _ = rotate_block_offsets(offsets, block[BROT])
            block_positions = []
            for offset in offsets:
                block_positions.append([
                    block[BX] + offset[0],
                    block[BY] + offset[1],
                    block[BZ] + offset[2]
                ])

            positions.append(block_positions)

        return positions

    def get_at_pos(track, pos):
        for block in track:
            if list(block[BX:BZ+1]) == pos:
                return block
        return None

    occupied = occupied(track)

    start_block = None
    for block in track:
        if is_start(get_block_name(block[BID])):
            start_block = block
            break

    if not start_block:
        return []

    queue = track[:]
    queue.remove(start_block)

    current_pos = list(start_block[BX:BZ+1])
    s = [start_block]

    for i, block_positions in enumerate(occupied):
        for j, pos in enumerate(block_positions):
            if pos == current_pos:
                del occupied[i]

    while len(queue) > 0 and len(occupied) > 0:
        current = get_at_pos(track, current_pos)
        if current and current[BID] == 6:
            if current[BROT] == 0:
                neighbour = get_at_pos(
                    queue, [current_pos[0], current_pos[1], current_pos[2] + 1])
            elif current[BROT] == 1:
                neighbour = get_at_pos(
                    queue, [current_pos[0] - 1, current_pos[1], current_pos[2]])
            elif current[BROT] == 2:
                neighbour = get_at_pos(
                    queue, [current_pos[0], current_pos[1], current_pos[2] - 1])
            elif current[BROT] == 3:
                neighbour = get_at_pos(
                    queue, [current_pos[0] + 1, current_pos[1], current_pos[2]])

            if neighbour:
                current_pos = list(neighbour[BX:BZ+1])
                try:
                    index = queue.index(
                        (current[0], neighbour[0], neighbour[1], neighbour[2], current[4]))
                    s.append(queue.pop(index))
                    del occupied[index]
                    continue
                except ValueError:
                    pass

        m = 1000
        cindex = (0, 0)
        for i, block_positions in enumerate(occupied):
            for j, pos in enumerate(block_positions):
                d = dist(pos, current_pos)
                if d < m:
                    m = d
                    cindex = (i, j)

        m = 0
        findex = cindex
        for j, pos in enumerate(occupied[cindex[0]]):
            d = dist(pos, current_pos)
            if d > m:
                m = d
                findex = (cindex[0], j)

        s.append(queue.pop(cindex[0]))

        current_pos = occupied[findex[0]][findex[1]]
        del occupied[cindex[0]]
    return s


def fit_position_scaler(train_data):
    scaler = MinMaxScaler()
    X = [[0, 0, 0]]

    for i, entry in enumerate(train_data):
        track = entry[1]
        for j in range(len(track) - 1, -1, -1):
            current = track[j]
            prev = track[j - 1]

            X.append([
                current[BX] - prev[BX],
                current[BY] - prev[BY],
                current[BZ] - prev[BZ]
            ])

            train_data[i][1][j] = (current[BID], X[-1][0],
                                   X[-1][1], X[-1][2], current[BROT])

        block = track[0]
        train_data[i][1][0] = (block[BID], 0, 0, 0, block[BROT])

    scaler.fit(X)
    return scaler


def create_pattern_data(train_data):
    patterns = {}
    for entry in train_data:
        track = entry[1]
        for i in range(1, len(track) - 1):
            prev = track[i - 1]
            prev = (prev[BID], 0, 0, 0, prev[BROT])
            n = track[i]

            rotated = rotate_track_tuples([prev, n], (4 - prev[BROT]) % 4)

            prev = rotated[0]
            n = rotated[1]
            n = (n[BID], n[BX] - prev[BX], n[BY] -
                 prev[BY], n[BZ] - prev[BZ], n[BROT])

            prev = (prev[BID], 0, 0, 0, prev[BROT])

            if not (prev, n) in patterns:
                patterns[(prev, n)] = 1
            else:
                patterns[(prev, n)] += 1

    return patterns
