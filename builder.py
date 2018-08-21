import numpy as np
import random
import blocks as bl
from blocks import BID, BX, BY, BZ, BROT
import pickle

POS_LEN = 3
ROTATE_LEN = 4

class Builder(object):
    def __init__(self, block_model, position_model, scaler, lookback, seed_data, use_softmax_backend):
        self.block_model = block_model
        self.position_model = position_model
        self.scaler = scaler
        self.lookback = lookback
        self.seed_data = seed_data
        self.track = []

        if use_softmax_backend:
            self.block_to_vec = self.block_to_vec_softmax
            self.unpack_position_preds = self.unpack_position_preds_softmax
            self.intersects_track = self.intersects_track_softmax
            self.inp_len = len(bl.BLOCKS) + (32 * POS_LEN) + ROTATE_LEN
        else:
            self.block_to_vec = self.block_to_vec_vector
            self.unpack_position_preds = self.unpack_position_preds_vector
            self.intersects_track_vector
            self.inp_len = len(bl.BLOCKS) + (POS_LEN) + ROTATE_LEN

    @staticmethod
    def random_start_block():
        return (bl.START_LINE_BLOCK, random.randrange(10, 22), random.randrange(11, 23), random.randrange(10, 22), random.randrange(0, 4))

    @staticmethod
    def sample(preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    # def build(self, track_len, use_seed=True, seed_length=3, save_path=None, seed_idx=-1):
    #     X = np.zeros((1, self.lookback, bl.INPUT_LEN), dtype=np.bool)

    #     track = []
        
    #     if use_seed:
    #         if seed_idx != -1:
    #             idx = seed_idx
    #         else:
    #             idx = random.randrange(0, len(self.seed_data))
    #         seed_sequence = self.seed_data[idx][1]
    #         # r = random.randrange(0, len(seed_sequence))
    #         r = 0
    #         seed = seed_sequence[r:r + seed_length]
    #         # print('Seed: index {} ({} blocks): {}'.format(idx, seed_length, seed_sequence[r:r + seed_length + 5]))
    #         track.extend(seed)
    #         seed.reverse()
    #         for i in range(len(seed)):
    #             X[0][-i - 1] = bl.vectorize_block(seed[i], True)
    #     else:
    #         start = self.random_start_block()
    #         track.append(start)
    #         X[0][-1] = bl.vectorize_block(start, True)

    #     blocks_len = len(bl.BLOCKS)
    #     for i in range(track_len):
    #         if i == track_len - 1:
    #             # Put finish
    #             X[0][-1][-1] = 1

    #         # temp = 1.0
    #         # temp = random.uniform(0.8, 1.0)

    #         preds = self.model.predict(X)[0]
    #         # bid = self.sample(preds[:blocks_len], temp) + 1

    #         bid = np.argmax(preds[:blocks_len]) + 1
    #         px = preds[blocks_len:blocks_len + 32]
    #         py = preds[blocks_len + 32:blocks_len + 32 + 32]
    #         pz = preds[blocks_len + 32 + 32:blocks_len+32+32+32]
    #         pr = preds[blocks_len+32+32+32:]

    #         x = np.argmax(px)
    #         y = np.argmax(py) + 1
    #         z = np.argmax(pz)
    #         r = np.argmax(pr)

    #         # x = np.flip(np.argsort(px), 0)[0]
    #         # y = np.flip(np.argsort(py), 0)[0] + 1
    #         # z = np.flip(np.argsort(pz), 0)[0]
    #         # r = np.argmax(pr)

    #         track.append((bid, x, y, z, r))

    #         for i in range(1, self.lookback):
    #             X[0][i - 1] = X[0][i]

    #         X[0][-1] = bl.vectorize_block(track[-1], True)

    #     if save_path:
    #         pickle.dump(track, open(save_path, 'w+'))

    #     return track

    @staticmethod
    def block_to_vec_vector(inp_len, block, scaler, encode_pos=True):
        if block[0] == 0:
            return [0] * inp_len

        bid_vec = bl.one_hot_bid(block[0])
        if encode_pos:
            pos_vec = scaler.transform([block[1:4]])[0]
            rot_vec = bl.one_hot_rotation(block[4])
        else:
            pos_vec = [0] * POS_LEN
            rot_vec = [0] * ROTATE_LEN

        return bid_vec + list(pos_vec) + rot_vec

    @staticmethod
    def block_to_vec_softmax(inp_len, block, scaler, encode_pos=True):
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
        next_block = self.sample(block_preds, random.uniform(0.4, 1.0)) + 1
        # next_block = np.argmax(block_preds) + 1

        X_position[0][-1] = self.block_to_vec(self.inp_len, self.track[-1], self.scaler, True)

        for i in range(1, self.lookback):
            X_block[0][i - 1] = X_block[0][i]

        for i in range(1, self.lookback):
            X_position[0][i - 1] = X_position[0][i]

        X_block[0][-1] = bl.one_hot_bid(next_block)
        X_position[0][-1] = self.block_to_vec(self.inp_len, (next_block, 0, 0, 0, 0), self.scaler, False)

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
            X_position[0][-i - 1] = self.block_to_vec(self.inp_len, seed[i], self.scaler, True)

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

    def lower_track(self):
        min_y = self.track[0][BY]

        for block in self.track[1:]:
            min_y = min(min_y, block[BY])

        if min_y == 1:
            return

        offset = min_y - 1
        for i in range(len(self.track)):
            block = self.track[i]
            self.track[i] = (block[BID], block[BX], self.track[i][BY] - offset, block[BZ], block[BROT])

    def build(self, track_len, use_seed=True):
        self.track = []
        X_block = np.zeros((1, self.lookback, len(bl.BLOCKS)), dtype=np.bool)
        X_position = np.zeros((1, self.lookback, self.inp_len))

        if use_seed:
            seed = self.sample_seed(3)
            self.track.extend(seed)
            self.encode_seed(seed[:], X_block, X_position)
        else:
            self.track.append((14, 30, 2, 3, 0))
            X_block[0][-1] = bl.one_hot_bid(self.track[-1][BID])
            X_position[0][-1] = self.block_to_vec(self.inp_len, self.track[-1], self.scaler, True)

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
            if self.intersects_track(next_block):
                fails += 1
                continue

            X_block = new_X_block
            X_position = new_X_positon

            prev_X_position = X_position[:]
            prev_X_block = X_block[:]
            self.track.append(next_block)
            print(len(self.track))

        if self.block_to_vec == self.block_to_vec_vector:
            # track_size = self.get_track_size()
            # sx = random.randrange(0, 32 - track_size[0])
            # sy = random.randrange(0, 32 - track_size[1])
            # sz = random.randrange(0, 32 - track_size[2])
            sx, sy, sz = (15, 5, 15)

            self.track = self.decoded_track(start_pos=(sx, sy, sz))
            self.lower_track()
        pickle.dump(self.track, open('generated-track.bin', 'w+'))
        return self.track, X_position
