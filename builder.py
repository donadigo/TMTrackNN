import random
from keras.models import Sequential

import numpy as np

from block_utils import BID, BROT, BX, BY, BZ, one_hot_bid, block_to_vec
from pygbx.stadium_blocks import STADIUM_BLOCKS
from block_utils import START_LINE_BLOCK, FINISH_LINE_BLOCK, GROUND_BLOCKS
from pygbx.headers import Vector3
from track_utils import intersects, occupied_track_vectors, rotate_track_tuples
from gamemap import GameMap
from tech_block_weights import TECH_BLOCK_WEIGHTS

POS_LEN = 3
ROTATE_LEN = 4


class Builder(object):
    '''
    The Builder class implements the main building loop that consists of:
        1. predicting the next block type
        2. predicting the position and rotation of the next block that is going to be placed
        3. validating model output with provided pattern data
        4. validating track characteristics such as its size and placement
        5. backtracking if the networks get stuck and cannot predict a good enough outcome
        6. Reporting progress to the user of the class

    Args:
        block_model (keras.models.Sequential): the block model to use
        position_model (keras.models.Sequential): the positionmodel model to use
        lookback (int): how many previous blocks are fed into the network at a time
        seed_data (list): optional sample data to evaluate network preformance
        temperature (float): the temperature to use
    '''
    def __init__(self, block_model: Sequential, position_model: Sequential, lookback: int,
                seed_data: list, pattern_data: dict, scaler: object, temperature: float=1.2):
        self.block_model = block_model
        self.position_model = position_model
        self.lookback = lookback
        self.seed_data = seed_data
        self.pattern_data = pattern_data
        self.scaler = scaler
        self.inp_len = len(STADIUM_BLOCKS) + POS_LEN + ROTATE_LEN
        self.temperature = temperature
        self.running = False
        self.gmap = None

    @staticmethod
    def random_start_block():
        '''
        Returns a start block in a random direction.

        Returns:
            tuple: the randomized start block
        '''
        return (START_LINE_BLOCK, 0, 0, 0, random.randrange(0, 4), 0)

    @staticmethod
    def unpack_position_preds_vector(preds: tuple):
        '''
        Unpacks position and rotation prediction from the model prediction.

        Args:
            preds (tuple): (position_preds: np.array, rotation_preds: np.array)

        Returns:
            tuple: the unpacked position and rotation prediction
        '''
        pos_vec = [int(round(axis)) for axis in preds[0][0]]
        pos_rot = np.argmax(preds[1][0])
        return pos_vec, pos_rot

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

    def predict_next_block(self, X_block: np.array, X_position: np.array, block_override: int=-1,
                        blacklist: list=[], block_preds: np.array=None):
        '''
        Predicts the next block in the main building loop.

        Asks the block model for prediction of the next block type
        based on the encoded previous blocks and then feeds the
        output to the position model.

        Args:
            X_block (np.array): encoded block types of shape (1, lookback, blocks_len)
            X_position (np.array): encoded blocks of shape (1, lookback, inp_len)
            block_override (int): the block type to use instead of predicting it
            blacklist (list): the list containing block IDs that should not 
                              be considered when sampling
            block_preds (list): cached array of block predictions from the previous
                                prediction, used when backtracking
            
            Returns:
                tuple: (predicted_block: tuple, block_preds: np.array)
        '''
        if block_override != -1:
            next_block = block_override
        else:
            if block_preds is None:
                block_preds = self.block_model.predict(X_block)[0]
                block_preds = block_preds * TECH_BLOCK_WEIGHTS

            block_preds[np.asarray(blacklist, dtype=int) - 1] = 0
            next_block = self.sample(block_preds) + 1

        X_position = np.roll(X_position, -1, 1)
        X_position[0, -1] = block_to_vec((next_block, 0, 0, 0, 0), self.inp_len, len(STADIUM_BLOCKS), self.scaler, False)

        pos_preds = self.position_model.predict(X_position)
        pos_vec, pos_rot = self.unpack_position_preds_vector(pos_preds)
        return (next_block, *pos_vec, pos_rot), block_preds

    def sample_seed(self, seed_len: int) -> list:
        '''
        Generates a random sample from seed data. Used for
        evaluating network performance when completing e.g training data samples.

        Args:
            seed_len (int): track length to seed
        
        Returns:
            list: the track from the seed
        '''
        seed_idx = random.randrange(0, len(self.seed_data))
        seed = self.seed_data[seed_idx][1][:seed_len]
        return seed

    def score_prediction(self, prev_block: tuple, next_block: tuple) -> int:
        '''
        Scores the prediction using the previous block and the block that
        was just placed, using pattern data.

        Args:
            prev_block (tuple): the previous block
            next_block (tuple): the block that was just placed

        Returns:
            int: the prediction score
        '''
        prev_block = (prev_block[BID], 0, 0, 0, prev_block[BROT])
        prev_block, next_block = rotate_track_tuples([prev_block, next_block], 4 - prev_block[BROT] % 4)

        next_block = (next_block[BID], next_block[BX] - prev_block[BX], next_block[BY] -
                      prev_block[BY], next_block[BZ] - prev_block[BZ], next_block[BROT])

        target = (prev_block[BID], next_block)
        try:
            return self.pattern_data[target]
        except KeyError:
            return 0

    def prepare_inputs(self):
        '''
        Prepares the block and position vector encodings used by predict_next_block.

        Returns:
            tuple: (X_block: np.array, X_position: np.array)
        '''
        X_block = np.zeros((1, self.lookback, len(STADIUM_BLOCKS)), dtype=np.bool)
        X_position = np.zeros((1, self.lookback, self.inp_len))

        blocks = self.gmap.track[-self.lookback:]
        i = -1
        for block in reversed(blocks):
            X_position[0, i] = block_to_vec(block, self.inp_len, len(STADIUM_BLOCKS), self.scaler, True)
            X_block[0, i] = one_hot_bid(block[BID], len(STADIUM_BLOCKS))
            i -= 1

        return X_block, X_position

    def stop(self):
        '''
        Stops the building process.
        '''
        self.running = False

    def build(self, track_len: int, use_seed: bool=False, failsafe: bool=True, verbose: bool=True,
            put_finish: bool=True, progress_callback=None, map_size: tuple=(20, 8, 20)):
        '''
        Builds the track according to the parameters.

        Args:
            track_len (int): the track length, in blocks
            use_seed (bool): whether to use a random seed from the seed data
            failsafe (bool): whether to enable various checking heuristics
            verbose (bool): print additional information while building
            put_finish (bool): whether to put a finish as the last block
            progress_callback: a function that is called whenever a new block is placed
            map_size (tuple): the map size to build the track in
        
        Returns:
            list: the resulting track
        '''
        self.running = True

        fixed_y = random.randrange(1, 7)
        if not self.gmap:
            self.gmap = GameMap(Vector3(map_size[0], map_size[1], map_size[2]), Vector3(0, fixed_y, 0))

        if use_seed and self.seed_data:
            self.gmap.track = self.sample_seed(3)
        elif len(self.gmap) == 0:
            self.gmap.add(self.random_start_block())

        self.gmap.update()

        blacklist = []
        current_block_preds = None
        while len(self.gmap) < track_len:
            if not self.running:
                return None

            end = len(self.gmap) == track_len - 1
            if len(blacklist) >= 10 or (len(blacklist) == 1 and end):
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

            block_override = FINISH_LINE_BLOCK if end and put_finish else -1

            next_block, current_block_preds = self.predict_next_block(
                X_block[:], X_position[:], block_override=block_override, blacklist=blacklist, block_preds=current_block_preds
            )

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
