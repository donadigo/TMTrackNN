import numpy as np
import random
import blocks as bl
from blocks import BID, BX, BY, BZ, BROT
from block_offsets import intersects
import pickle

POS_LEN = 3
ROTATE_LEN = 4

class Builder(object):
    def __init__(self, block_model, position_model, lookback, seed_data, use_softmax_backend):
        self.block_model = block_model
        self.position_model = position_model
        self.lookback = lookback
        self.seed_data = seed_data
        self.track = []

        if use_softmax_backend:
            self.block_to_vec = self.block_to_vec_softmax
            self.unpack_position_preds = self.unpack_position_preds_softmax
        else:
            self.block_to_vec = self.block_to_vec_vector
            self.unpack_position_preds = self.unpack_position_preds_vector

        self.inp_len = len(bl.BLOCKS) + (32 * POS_LEN) + ROTATE_LEN

    @staticmethod
    def random_start_block():
        return (bl.START_LINE_BLOCK, random.randrange(10, 22), random.randrange(1, 11), random.randrange(10, 22), random.randrange(0, 4))

    @staticmethod
    def sample(preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    @staticmethod
    def block_to_vec_vector(inp_len, block, encode_pos=True):
        if block[0] == 0:
            return [0] * inp_len

        bid_vec = bl.one_hot_bid(block[0])
        if encode_pos:
            pos_vec = bl.one_hot_pos(block[BX]) + bl.one_hot_pos(block[BY], True) + bl.one_hot_pos(block[BZ])
            rot_vec = bl.one_hot_rotation(block[4])
        else:
            pos_vec = [0] * (POS_LEN * 32)
            rot_vec = [0] * ROTATE_LEN

        return bid_vec + list(pos_vec) + rot_vec

    @staticmethod
    def block_to_vec_softmax(inp_len, block, encode_pos=True):
        if block[0] == 0:
            return [0] * inp_len

        bid_vec = bl.one_hot_bid(block[0])
        if encode_pos:
            pos_vec = bl.one_hot_pos(block[BX]) + bl.one_hot_pos(block[BY], True) + bl.one_hot_pos(block[BZ])
            rot_vec = bl.one_hot_rotation(block[4])
        else:
            pos_vec = [0] * (POS_LEN * 32)
            rot_vec = [0] * ROTATE_LEN

        return bid_vec + list(pos_vec) + rot_vec

    @staticmethod
    def unpack_position_preds_vector(preds):
        pos_vec = [int(round(axis)) for axis in preds[0][0]]
        pos_rot = np.argmax(preds[1][0])
        return pos_vec, pos_rot

    @staticmethod
    def unpack_position_preds_softmax(preds):
        pos_x = np.argmax(preds[0][0])
        pos_y = np.argmax(preds[1][0]) + 1
        pos_z = np.argmax(preds[2][0])
        pos_rot = np.argmax(preds[3][0])
        print (preds[0][0][pos_x], preds[1][0][pos_y - 1], preds[2][0][pos_z])
        return (pos_x, pos_y, pos_z), pos_rot
        
    def intersects_track_vector(self, tblock):
        d = self.decoded_track()
        prev = d[-1]
        d.append((tblock[BID],
                tblock[BX] + prev[BX],
                tblock[BY] + prev[BY],
                tblock[BZ] + prev[BZ],
                tblock[BROT]
        ))

        s = d[-1][BX:BZ+1]
        for block in d[:-1]:
            if block[BX:BZ+1] == s:
                return True

        return False
 
    def intersects_track_softmax(self, tblock):
        for block in self.track:
            if block[BX:BZ+1] == tblock[BX:BZ+1]:
                return True
        
        return False

    def predict_next_block(self, X_block, X_position):
        block_preds = self.block_model.predict(X_block)[0]
        next_block = self.sample(block_preds, 1.2) + 1

        X_position[0][-1] = self.block_to_vec(self.inp_len, self.track[-1], True)

        for i in range(1, self.lookback):
            X_block[0][i - 1] = X_block[0][i]

        for i in range(1, self.lookback):
            X_position[0][i - 1] = X_position[0][i]

        X_block[0][-1] = bl.one_hot_bid(next_block)
        X_position[0][-1] = self.block_to_vec(self.inp_len, (next_block, 0, 0, 0, 0), False)

        pos_preds = self.position_model.predict(X_position)
        pos_vec, pos_rot = self.unpack_position_preds(pos_preds)
        return (next_block, pos_vec[0], pos_vec[1], pos_vec[2], pos_rot), X_block, X_position

    def sample_seed(self, seed_len):
        seed_idx = random.randrange(0, len(self.seed_data))
        seed = self.seed_data[seed_idx][1][:seed_len]
        return seed
    
    def encode_seed(self, seed, X_block, X_position):
        seed.reverse()
        for i in range(len(seed)):
            X_block[0][-i - 1] = bl.one_hot_bid(seed[i][BID])

        for i in range(len(seed)):
            X_position[0][-i - 1] = self.block_to_vec(self.inp_len, seed[i], True)

    def decoded_track(self, start_pos=(0, 0, 0)):
        d = self.track[:]
        d[0] = (d[0][BID], start_pos[0], start_pos[1], start_pos[2], d[0][BROT])
        for i in range(1, len(d)):
            block = d[i]
            prev = d[i - 1]
            d[i] = (block[BID],
                    block[BX] + prev[BX],
                    block[BY] + prev[BY],
                    block[BZ] + prev[BZ],
                    block[BROT])
        return d

    def get_track_size(self):
        d = self.decoded_track()
        min_x, min_y, min_z = d[0][BX:BZ+1]
        max_x, max_y, max_z = d[0][BX:BZ+1]

        for block in d[1:]:
            min_x = min(block[BX], min_x)
            min_y = min(block[BY], min_y)
            min_z = min(block[BZ], min_z)

            max_x = max(block[BX], max_x)
            max_y = max(block[BY], max_y)
            max_z = max(block[BZ], max_z)

        return abs(max_x - min_x) + 1, abs(max_y - min_y) + 1, abs(max_z - min_z) + 1

    @staticmethod
    def dist(x,y):
        return np.sqrt(np.sum((x-y) ** 2))


    def build(self, track_len, use_seed=False, start_seed=[]):
        self.track = []
        X_block = np.zeros((1, self.lookback, len(bl.BLOCKS)), dtype=np.bool)
        X_position = np.zeros((1, self.lookback, self.inp_len))

        if len(start_seed) > 0:
            if use_seed:
                seed = self.sample_seed(3)
            else:
                seed = start_seed[:]

            self.track.extend(seed)
            self.encode_seed(seed[:], X_block, X_position)
        else:
            self.track.append(self.random_start_block())
            X_block[0][-1] = bl.one_hot_bid(self.track[-1][BID])
            X_position[0][-1] = self.block_to_vec(self.inp_len, self.track[-1], True)

        prev_X_position = X_position[:]
        prev_X_block = X_block[:]
        
        fails = 0
        while len(self.track) < track_len:
            if fails >= 20:
                print('More than 20 fails, going back.')
                X_position = prev_X_position[:]
                X_block = prev_X_block[:]
                fails = 0

            next_block, new_X_block, new_X_positon = self.predict_next_block(X_block[:], X_position[:])
            if self.unpack_position_preds == self.unpack_position_preds_vector:
                last_block = self.track[-1]
                next_block = (next_block[0],
                            next_block[1] + last_block[1],
                            next_block[2] + last_block[2],
                            next_block[3] + last_block[3],
                            next_block[4])

            if intersects(self.track, next_block):
                fails += 1
                continue

            if self.dist(np.array(next_block[BX:BZ+1]), np.array(self.track[-1][BX:BZ+1])) > 4:
                fails += 1
                continue

            X_block = new_X_block
            X_position = new_X_positon

            prev_X_position = X_position[:]
            prev_X_block = X_block[:]
            self.track.append(next_block)
            print(len(self.track))

        pickle.dump(self.track, open('generated-track.bin', 'wb+'))
        return self.track
