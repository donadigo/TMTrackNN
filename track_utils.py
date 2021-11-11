import numpy as np
from pygbx.stadium_blocks import STADIUM_BLOCKS
from block_utils import DYNAMIC_GROUND_OFFSETS, CONNECT_MAP, BID, BROT, BX, BY, BZ, BFLAGS, block_from_tup, get_block_name, block_to_tup
from pygbx.headers import Vector3
from pygbx.stadium_block_offsets import STADIUM_BLOCK_OFFSETS
from sklearn.preprocessing import MinMaxScaler


def rotate(vec: list, rot: int) -> list:
    '''
    Rotates a 3D vector by a given cardinal rotation,
    leaving the Y component unchaged. 

    Args:
        vec (list): the vector to rotate
        rot (int): the cardinal rotation to rotate by

    Returns:
        list: the rotated vector
    '''
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


def rotate_track(blocks: list, rotation: int) -> list:
    '''
    Rotates the entire track by a given cardinal rotation.
    The rotation happens inside the standard stadium arena size (32, 32, 32).

    The rotation factors in the fact that blocks may
    occupy more than one spot on the map, by rotating
    the block offsets first and then adding the maximum X and Z component
    offset to the original position rotation.

    Args:
        blocks (list): a list of pygbx.MapBlock's
        rotation (int): the cardinal rotation to rotate by

    Returns:
        list: the rotated blocks
    '''
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


def rotate_track_tuples(tblocks: list, rotation: int) -> list:
    '''
    A wrapper for rotate_track that accepts and returns raw block tuples instead.

    Args:
        blocks (list): a list of tuples representing each block
        rotation (int): the cardinal rotation to rotate by

    Returns:
        list: the rotated blocks
    '''
    blocks = [block_from_tup(tup) for tup in tblocks]
    return [block_to_tup(block) for block in rotate_track(blocks, rotation)]


def get_cardinal_position(pos: list, direction: int) -> list:
    '''
    Gets a position offseted by one place by a given direction.

    Args:
        pos (list): the position to offset
        direction (int): the direction to offset by
    
    Returns:
        list: the offseted position
    '''
    if direction == 0:
        return [pos[0], pos[1], pos[2] + 1]
    elif direction == 1:
        return [pos[0] - 1, pos[1], pos[2]]
    elif direction == 2:
        return [pos[0], pos[1], pos[2] - 1]
    elif direction == 3:
        return [pos[0] + 1, pos[1], pos[2]]

    return pos


def populate_flags(track: list) -> list:
    '''
    Populates block flags for saving the blocks into a Gbx file.

    Each block contains additional flags that indicate e.g
    to which other road pieces a single road piece is connected,
    or whether a block is on the ground.

    Args:
        track (list): the block tuples to populate flags for

    Returns:
        list: the populated block tuples
    '''
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


def is_on_ground(block: tuple) -> bool:
    '''
    Determines whether the block is on the ground.

    Gets the offsets for the block and checks if any of them
    is on the level 1.

    Args:
        block (tuple): the block to check
    
    Returns:
        bool: whether the block is on the ground
    '''
    try:
        offsets = STADIUM_BLOCK_OFFSETS[get_block_name(block[BID], STADIUM_BLOCKS)]
        for offset in offsets:
            if block[BY] + offset[1] == 1:
                return True
    except KeyError:
        pass

    return False


def rotate_block_offsets(offsets: list, rot: int) -> tuple:
    '''
    Rotates given block offsets and returns by which X and Z
    offsets to move the block after the rotation for it to stay
    in its original position.

    Args:
        offsets (list): the offsets to rotate
        rot (int): the cardinal rotation to rotate by

    Returns:
        tuple: (offsets: list, x_offset: int, y_offset: int)
    '''
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


def occupied_track_positions(track: list) -> dict:
    '''
    Produces a dict of each block and its occupied positions.

    Some blocks may have different offsets depending on whether
    they are on the ground or not.

    Args:
        track (list): the list of block tuples
    
    Returns:
        dict: blocks as keys and their occupied positions as values
    '''
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


def occupied_track_vectors(track: list) -> list:
    '''
    Gets occupied positions of a track in one contiguous vector.
    See occupied_track_positions.

    Args:
        track (list): the list of block tuples
    
    Returns:
        list: the vectors of occupied block positions
    '''
    occ = occupied_track_positions(track)
    vectors = []
    for p in list(occ.values()):
        vectors.extend(p)

    return vectors


def intersects(track: list, block: tuple) -> bool:
    '''
    Checks if the block collides in any way with a given track.

    Args:
        track (list): the list of block tuples
        block (tuple): the block to check

    Returns:
        bool: whether the track and block collide
    '''
    track_offsets = occupied_track_vectors(track)
    block_offsets = occupied_track_vectors([block])

    for block_off in block_offsets:
        for track_off in track_offsets:
            if block_off == track_off:
                return True
    return False


def fit_data_scaler(train_data: list) -> MinMaxScaler:
    '''
    Fits an sklearn.preprocessing.MinMaxScaler for relative positions
    that are used for feeding the position data into the position network.

    Args:
        train_data (list): the list consisting of data entries (track_name: str, block_list: list)
    
    Returns:
        sklearn.preprocessing.MinMaxScaler: the scaler after fitting
    '''
    scaler = MinMaxScaler()
    X = []

    for entry in train_data:
        v = vectorize_track(entry[1])
        for block in v:
            X.append(block[BX:BZ+1])

    scaler.fit(X)
    return scaler


def vectorize_track(track: list) -> list:
    '''
    "Vectorizes" a track, by replacing absolute map
    coordinates with relative coordinates from the previous block.
    This makes the first block in the sequence start at (0, 0, 0).

    Args:
        track (list): the list of block tuples
    
    Returns:
        list: the vectorized block tuples
    '''
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

    if track and v:
        block = track[0]
        v[0] = (block[BID], 0, 0, 0, block[BROT], block[BFLAGS])

    return v


def create_pattern_data(train_data: list) -> dict:
    '''
    Creates "pattern" data, used as a verification heuristic on
    top of neural networks.

    The pattern data is used to verify temporal coherence between the previous
    block and the block that was just placed. The result is a dictionary of
    ((prev_block_id, next): occurences) entries, where the (prev_block_id, next) tuple represent
    the two blocks. "prev_block_id" represents the previous block ID and "next" represents
    the vectorized block that was placed.
    
    Occurences is how many each configuration appeared in the provided train data.
    The entries are rotation invariant so that the specific rotation is not taken
    into account when counting up occurences.

    Args:
        train_data (list): the training data
    
    Returns:
        dict: the pattern data
    '''
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
