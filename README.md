# TMTrackNN
Building TrackMania tracks with neural networks.

This is a hobby project for fun to learn Python and also to learn how neural nets work. It is not meant to work and probably never will.

## What?
The aim is to generate new maps, tracks using NN's for a racing game called [TrackMania](https://www.trackmania.com/). I created this project a while ago for fun and mostly for educational purposes.

## Dependencies
* Python 2.7
* Keras
* python-lzo (through pip)
* numpy
* Not required: Gtk+3 and GLib for track visualization

## Dataset
This repo doesn't contain the dataset itself used to train the models in the `models/` directory as it is unusual to provide entire datasets with code in one repo. There is however a preprocessed version of the dataset used in the `data/train_data.pkl` file that you can use for futher training.

The file contains roughly 3000 tech tracks downloaded directly from [TMX](https://tmnforever.tm-exchange.com/) and preprocessed such that they contain only the simplified version of tracks of each map. The maps themselves were downloaded using these filters: type: tech, order: awards (most), length: ~= 1m.

## Training
It is recommended to have a dedicated GPU for training the nets, otherwise training process will be very slow.

There are 2 neural networks involved in the training process, both are LSTM networks.
* `train_blocks.py` trains a network that predicts what next block type to put next given a sequence of blocks.

* `train_pos.py` trains a network that given sequence of blocks and their positions predicts the next position and rotation of the last block in the sequence (that was predicted by the block NN).

To train the block net with the trained model in the `models/` directory:
```
python -i train_blocks.py -g -l models/block-model.h5
```

To train the position net with the trained model in the `models/` directory:
```
python -i train_pos.py -g -l models/position-model.h5
```

Unfortunately both files require manually stopping the training process and saving the models using `model.save('model-filename.h5')`, at some point there will probably be model checkpointing built in to the argument options.

## Generating new tracks
The process here is also manual and needs more work / documentation. At the moment it's possible to generate a new track using `builder.py` and save the track to .Gbx using `savegbx.py`.