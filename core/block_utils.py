BID, BX, BY, BZ, BROT, BFLAGS = range(6)
EMPTY_BLOCK = (0, 0, 0, 0, 0)

def one_hot_bid(bid, nclasses):
    arr = [0] * nclasses
    if bid != 0:
        arr[bid - 1] = 1
    return arr

def one_hot_rotation(r):
    arr = [0] * 4
    arr[r] = 1
    return arr


def block_to_vec(block, inp_len, num_classes, scaler, encode_pos=True):
    if block[0] == 0:
        return [0] * inp_len

    bid_vec = one_hot_bid(block[0], num_classes)
    if encode_pos:
        pos_vec = scaler.transform([block[BX:BZ+1]])[0]
        rot_vec = one_hot_rotation(block[BROT])
    else:
        pos_vec = [-1, -1, -1]
        rot_vec = [-1, -1, -1, -1]

    return bid_vec + list(pos_vec) + rot_vec


def pad_block_sequence(seq, maxlen):
    pad = [EMPTY_BLOCK] * (maxlen - len(seq))
    return pad + seq


def get_block_name(bid, blocks):
    for name, _bid in blocks.items():
        if _bid == bid:
            return name
    return None
