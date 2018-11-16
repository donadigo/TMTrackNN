import pickle
import random

import numpy as np

import blocks as bl
from track_utils import intersects, occupied_track_vectors, rotate_track_tuples, dist
from blocks import BID, BROT, BX, BY, BZ
from tech_block_weights import TECH_BLOCK_WEIGHTS

POS_LEN = 3
ROTATE_LEN = 4


class Builder(object):
    def __init__(self, block_model, position_model, lookback, seed_data, pattern_data, scaler, temperature=1.2):
        self.block_model = block_model
        self.position_model = position_model
        self.lookback = lookback
        self.seed_data = seed_data
        self.scaler = scaler
        self.track = []
        self.inp_len = len(bl.BLOCKS) + POS_LEN + ROTATE_LEN
        self.temperature = temperature
        self.pattern_data = pattern_data
        self.max_map_size = (32, 32, 32)
        self.running = False

    @staticmethod
    def random_start_block():
        return (bl.START_LINE_BLOCK, 0, 0, 0, random.randrange(0, 4))

    def sample(self, preds):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / self.temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    @staticmethod
    def block_to_vec(inp_len, block, scaler, encode_pos):
        if block[0] == 0:
            return [0] * inp_len

        bid_vec = bl.one_hot_bid(block[0])
        if encode_pos:
            pos_vec = scaler.transform([block[BX:BZ+1]])[0]
            rot_vec = bl.one_hot_rotation(block[4])
        else:
            pos_vec = [-1, -1, -1]
            rot_vec = [-1, -1, -1, -1]

        return bid_vec + list(pos_vec) + rot_vec

    @staticmethod
    def decoded_track(track, start_pos=(0, 0, 0)):
        d = track
        d[0] = (d[0][BID], start_pos[0], start_pos[1],
                start_pos[2], d[0][BROT])
        for i in range(1, len(d)):
            block = d[i]
            prev = d[i - 1]
            d[i] = (block[BID],
                    block[BX] + prev[BX],
                    block[BY] + prev[BY],
                    block[BZ] + prev[BZ],
                    block[BROT])
        return d

    def unpack_position_preds_vector(self, preds):
        pos_vec = [int(round(axis)) for axis in preds[0][0]]
        pos_rot = np.argmax(preds[1][0])
        return pos_vec, pos_rot

    def predict_next_block(self, X_block, X_position, block_override=-1, blacklist=[]):
        if block_override != -1:
            next_block = block_override
        else:
            block_preds = self.block_model.predict(X_block)[0]
            block_preds = block_preds * TECH_BLOCK_WEIGHTS
            block_preds = np.delete(
                block_preds, [bid - 1 for bid in blacklist])

            next_block = self.sample(block_preds) + 1

        for i in range(1, self.lookback):
            X_position[0][i - 1] = X_position[0][i]

        X_position[0][-1] = self.block_to_vec(self.inp_len,
                                              (next_block, 0, 0, 0, 0), self.scaler, False)

        pos_preds = self.position_model.predict(X_position)
        pos_vec, pos_rot = self.unpack_position_preds_vector(pos_preds)
        return (next_block, pos_vec[0], pos_vec[1], pos_vec[2], pos_rot)

    def sample_seed(self, seed_len):
        seed_idx = random.randrange(0, len(self.seed_data))
        seed = self.seed_data[seed_idx][1][:seed_len]
        return seed

    def score_prediction(self, prev_block, next_block):
        prev_block = (prev_block[BID], 0, 0, 0, prev_block[BROT])
        subtrack = rotate_track_tuples(
            [prev_block, next_block], 4 - prev_block[BROT] % 4)

        prev_block = subtrack[0]
        next_block = subtrack[1]
        next_block = (next_block[BID], next_block[BX] - prev_block[BX], next_block[BY] -
                      prev_block[BY], next_block[BZ] - prev_block[BZ], next_block[BROT])

        prev_block = (prev_block[BID], 0, 0, 0, prev_block[BROT])

        target = (prev_block, next_block)
        try:
            return self.pattern_data[target]
        except KeyError:
            return 0

    def prepare_inputs(self):
        X_block = np.zeros((1, self.lookback, len(bl.BLOCKS)), dtype=np.bool)
        X_position = np.zeros((1, self.lookback, self.inp_len))

        blocks = self.track[-self.lookback:]
        i = -1
        for block in reversed(blocks):
            X_block[0][i] = bl.one_hot_bid(block[BID])
            i -= 1

        i = -1
        for block in reversed(blocks):
            X_position[0][i] = self.block_to_vec(
                self.inp_len, block, self.scaler, True)
            i -= 1

        return (X_block, X_position)

    def position_track(self, track):
        occ = occupied_track_vectors(track)
        min_x = min(occ, key=lambda pos: pos[0])[0]
        min_y = min(occ, key=lambda pos: pos[1])[1] - 1
        min_z = min(occ, key=lambda pos: pos[2])[2]

        max_x = max(occ, key=lambda pos: pos[0])[0]
        max_y = max(occ, key=lambda pos: pos[1])[1] - 1
        max_z = max(occ, key=lambda pos: pos[2])[2]

        cx = 32 - (max_x - min_x + 1)
        if cx > 0:
            cx = random.randrange(0, cx)
        cz = 32 - (max_z - min_z + 1)
        if cz > 0:
            cz = random.randrange(0, cz)

        min_x = 0 if min_x >= 0 else min_x
        min_y = 0 if min_y >= 0 else min_y
        min_z = 0 if min_z >= 0 else min_z

        max_x = 0 if max_x < 32 else max_x - 31
        max_y = 0 if max_y < 32 else max_y - 31
        max_z = 0 if max_z < 32 else max_z - 31

        xoff = min_x - max_x
        yoff = min_y - max_y
        zoff = min_z - max_z

        p = []
        for block in track:
            p.append((block[BID], block[BX] - xoff + cx, block[BY] -
                      yoff, block[BZ] - zoff + cz, block[BROT]))

        return p

    def exceeds_map_size(self, track):
        occ = occupied_track_vectors(track)
        min_x = min(occ, key=lambda pos: pos[0])[0]
        min_y = min(occ, key=lambda pos: pos[1])[1]
        min_z = min(occ, key=lambda pos: pos[2])[2]

        max_x = max(occ, key=lambda pos: pos[0])[0]
        max_y = max(occ, key=lambda pos: pos[1])[1]
        max_z = max(occ, key=lambda pos: pos[2])[2]

        return max_x - min_x + 1 > self.max_map_size[0] or max_y - min_y + 1 > self.max_map_size[1] or max_z - min_z + 1 > self.max_map_size[2]

    def stop(self):
        self.running = False

    def get_y_locked(self):
        for block in self.track:
            if block[BID] in bl.GROUND_BLOCKS:
                return True

        return False

    def build(self, track_len, use_seed=False, failsafe=True, verbose=True, save=True, progress_callback=None):
        self.running = True

        # self.max_map_size = (random.randrange(
        #     12, 32+1), random.randrange(5, 10), random.randrange(12, 32+1))
        if use_seed:
            self.track = self.sample_seed(3)
        else:
            self.track = [self.random_start_block()]

        blacklist = []
        end = False
        current_min_y = 0
        while len(self.track) < track_len:
            if not self.running:
                return None

            if len(blacklist) >= 10 or (len(blacklist) == 1 and end):
                if verbose:
                    print('More than 10 fails, going back.')

                if end:
                    back = 5
                else:
                    back = random.randrange(1, 4)

                end_idx = min(len(self.track) - 1, back)
                if end_idx > 0:
                    del self.track[-end_idx:len(self.track)]

                end = False
                blacklist = []

            X_block, X_position = self.prepare_inputs()

            override_block = -1
            if end:
                override_block = bl.FINISH_LINE_BLOCK

            next_block = self.predict_next_block(
                X_block[:], X_position[:], override_block, blacklist=blacklist)

            decoded = self.decoded_track(
                self.track + [next_block], start_pos=(0, 0, 0))

            if failsafe:
                # Do not exceed map size
                if self.exceeds_map_size(decoded):
                    blacklist.append(next_block[BID])
                    continue

                if decoded[-1][BY] > current_min_y:
                    # TODO: encode ground bit in the position network
                    if decoded[-1][BID] == 6 and decoded[-2][BID] == 6 and dist(decoded[-1][BX:BZ+1], decoded[-2][BX:BZ+1]) > 1:
                        blacklist.append(next_block[BID])
                        continue

                    # Wants to put a ground block higher than ground
                    if next_block[BID] in bl.GROUND_BLOCKS:
                        blacklist.extend(bl.GROUND_BLOCKS)
                        continue

                if (intersects(decoded[:-1], decoded[-1]) or  # Overlaps the track
                        (next_block[BID] == bl.FINISH_LINE_BLOCK and not end)):  # Tries to put finish before desired track length
                    blacklist.append(next_block[BID])
                    continue

                if self.score_prediction(self.track[-1], next_block) < 5:
                    blacklist.append(next_block[BID])
                    continue

            blacklist = []

            occ = occupied_track_vectors([decoded[-1]])
            min_y_block = min(occ, key=lambda x: x[BY])[BY]
            if min_y_block < current_min_y:
                if self.get_y_locked():
                    blacklist.append(next_block[BID])
                    continue

                current_min_y = min_y_block

            self.track.append(next_block)
            if len(self.track) >= track_len - 1:
                end = True

            if progress_callback:
                progress_callback(len(self.track), track_len)

            if verbose:
                print(len(self.track))

        result_track = self.position_track(
            self.decoded_track(self.track, (0, 0, 0)))
        return result_track
