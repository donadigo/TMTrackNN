import pickle
import random
import time

import numpy as np

from core.block_utils import (BFLAGS, BID, BROT, BX, BY, BZ, one_hot_bid,
                              block_to_vec)
from core.stadium_blocks import STADIUM_BLOCKS, START_LINE_BLOCK, FINISH_LINE_BLOCK, GROUND_BLOCKS
from core.headers import Vector3
from core.track_utils import (intersects, occupied_track_vectors,
                              rotate_track_tuples)
from gamemap import GameMap
from tech_block_weights import TECH_BLOCK_WEIGHTS

POS_LEN = 3
ROTATE_LEN = 4


class Builder(object):
    def __init__(self, block_model, position_model, lookback, seed_data, pattern_data, scaler, temperature=1.2, reset=True):
        self.block_model = block_model
        self.position_model = position_model
        self.lookback = lookback
        self.seed_data = seed_data
        self.pattern_data = pattern_data
        self.scaler = scaler
        self.inp_len = len(STADIUM_BLOCKS) + POS_LEN + ROTATE_LEN
        self.temperature = temperature
        self.reset = reset
        self.running = False
        self.gmap = None

    @staticmethod
    def random_start_block():
        return (START_LINE_BLOCK, 0, 0, 0, random.randrange(0, 4), 0)

    # Source:
    # https://github.com/keras-team/keras/blob/master/examples/lstm_text_generation.py#L66
    # Helper function to sample an index from a probability array
    def sample(self, preds):
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / self.temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def unpack_position_preds_vector(self, preds):
        pos_vec = [int(round(axis)) for axis in preds[0][0]]
        pos_rot = np.argmax(preds[1][0])
        return pos_vec, pos_rot

    def predict_next_block(self, X_block, X_position, block_override=-1, blacklist=[], block_preds=None):
        if block_override != -1:
            next_block = block_override
        else:
            if block_preds is None:
                block_preds = self.block_model.predict(X_block)[0]
                block_preds = block_preds * TECH_BLOCK_WEIGHTS

            for bid in blacklist:
                block_preds[bid - 1] = 0

            next_block = self.sample(block_preds) + 1

        for i in range(1, self.lookback):
            X_position[0][i - 1] = X_position[0][i]

        X_position[0][-1] = block_to_vec((next_block, 0, 0, 0, 0), self.inp_len, len(STADIUM_BLOCKS), self.scaler, False)

        pos_preds = self.position_model.predict(X_position)
        pos_vec, pos_rot = self.unpack_position_preds_vector(pos_preds)
        return (next_block, pos_vec[0], pos_vec[1], pos_vec[2], pos_rot), block_preds

    def sample_seed(self, seed_len):
        seed_idx = random.randrange(0, len(self.seed_data))
        seed = self.seed_data[seed_idx][1][:seed_len]
        return seed

    def score_prediction(self, prev_block, next_block):
        prev_block = (prev_block[BID], 0, 0, 0, prev_block[BROT])
        normalized = rotate_track_tuples(
            [prev_block, next_block], 4 - prev_block[BROT] % 4)

        prev_block = normalized[0]
        next_block = normalized[1]
        next_block = (next_block[BID], next_block[BX] - prev_block[BX], next_block[BY] -
                      prev_block[BY], next_block[BZ] - prev_block[BZ], next_block[BROT])

        target = (prev_block[BID], next_block)
        try:
            return self.pattern_data[target]
        except KeyError:
            return 0

    def prepare_inputs(self):
        X_block = np.zeros((1, self.lookback, len(STADIUM_BLOCKS)), dtype=np.bool)
        X_position = np.zeros((1, self.lookback, self.inp_len))

        blocks = self.gmap.track[-self.lookback:]
        i = -1
        for block in reversed(blocks):
            X_position[0][i] = block_to_vec(block, self.inp_len, len(STADIUM_BLOCKS), self.scaler, True)
            X_block[0][i] = one_hot_bid(block[BID], len(STADIUM_BLOCKS))
            i -= 1

        return X_block, X_position

    def stop(self):
        self.running = False

    def build(self, 
        track_len,
        use_seed=False,
        failsafe=True,
        verbose=True,
        save=True,
        put_finish=True,
        progress_callback=None,
        map_size=(20, 8, 20)):

        self.running = True

        fixed_y = random.randrange(1, 7)
        if not self.gmap or self.reset:
            self.gmap = GameMap(
                Vector3(map_size[0], map_size[1], map_size[2]), Vector3(0, fixed_y, 0))

        if use_seed and self.seed_data:
            self.gmap.track = self.sample_seed(3)
        elif len(self.gmap) == 0:
            self.gmap.add(self.random_start_block())

        print(self.gmap.track)
        self.gmap.update()

        blacklist = []
        current_block_preds = None
        while len(self.gmap) < track_len:
            if not self.running:
                return None

            end = len(self.gmap) == track_len - 1
            if len(blacklist) >= 10 or (len(blacklist) == 1 and end) and self.reset:
                if verbose:
                    print('More than 10 fails, going back.')

                if len(self.gmap) > track_len - 5:
                    back = 5
                elif end:
                    back = 10
                else:
                    back = random.randrange(2, 6)

                end_idx = min(len(self.gmap) - 1, back)
                if end_idx > 0:
                    del self.gmap.track[-end_idx:len(self.gmap)]

                blacklist = []
                current_block_preds = None

            X_block, X_position = self.prepare_inputs()

            override_block = FINISH_LINE_BLOCK if end and put_finish else -1

            next_block, current_block_preds = self.predict_next_block(
                X_block[:], X_position[:], override_block, blacklist=blacklist, block_preds=current_block_preds)

            self.gmap.add(next_block)
            decoded = self.gmap.decoded

            if failsafe:
                # Do not exceed map size
                if self.gmap.exceeds_map_size():
                    blacklist.append(next_block[BID])
                    self.gmap.pop()
                    continue

                occ = occupied_track_vectors([decoded[-1]])
                if len(occ) > 0:
                    min_y_block = min(occ, key=lambda pos: pos.y).y
                else:
                    min_y_block = decoded[-1][BY]

                # If we are above the ground
                if min_y_block > 1 and next_block[BID] in GROUND_BLOCKS:
                    blacklist.extend(GROUND_BLOCKS)
                    self.gmap.pop()
                    continue

                if (intersects(decoded[:-1], decoded[-1]) or  # Overlaps the track
                        (next_block[BID] == FINISH_LINE_BLOCK and not end)):  # Tries to put finish before desired track length
                    blacklist.append(next_block[BID])
                    self.gmap.pop()
                    continue

                if self.score_prediction(self.gmap[-2], next_block) < 5:
                    blacklist.append(next_block[BID])
                    self.gmap.pop()
                    continue

            blacklist = []
            current_block_preds = None

            next_block = (next_block[BID], next_block[BX], next_block[BY],
                          next_block[BZ], next_block[BROT])

            if progress_callback:
                progress_callback(len(self.gmap), track_len)

            if verbose:
                print(len(self.gmap))

        result_track = self.gmap.center()
        result_track = [block for block in result_track if block[BID] != STADIUM_BLOCKS['StadiumGrass']]
        return result_track
