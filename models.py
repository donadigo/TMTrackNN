from keras.layers.core import Dense
from keras.layers import LSTM, concatenate
from keras.models import Input, Model, Sequential


def build_block_model(lookback: int, inp_len: int) -> Sequential:
    '''
    Builds the block network model.

    Args:
        lookback (int): the lookback length
        inp_len (int): length of the input

    Returns:
        keras.models.Sequential: the model
    '''
    model = Sequential()
    model.add(LSTM(512, input_shape=(lookback, inp_len), return_sequences=True))
    model.add(LSTM(512, return_sequences=True))
    model.add(LSTM(400))
    model.add(Dense(inp_len, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    return model


def build_pos_model(lookback: int, inp_len: int) -> Sequential:
    '''
    Builds the position network model.

    Args:
        lookback (int): the lookback length
        inp_len (int): length of the input

    Returns:
        keras.models.Sequential: the model
    '''
    inp = Input(shape=(lookback, inp_len))

    x = LSTM(512, return_sequences=True)(inp)
    x = LSTM(512, return_sequences=True)(x)

    x = concatenate([x, inp])
    x = LSTM(512, return_sequences=True)(x)
    x = LSTM(256)(x)
    
    pos = Dense(3, activation='linear', name='pos')(x)
    rot = Dense(4, activation='softmax', name='rot')(x)
    
    model = Model(inputs=inp, outputs=[pos, rot])
    model.compile(loss=['mse', 'categorical_crossentropy'],
                  optimizer='rmsprop')
    return model