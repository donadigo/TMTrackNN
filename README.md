# TMTrackNN
Building TrackMania tracks with neural networks.

This is a hobby project for fun to learn Python and also to learn how neural nets work. It is not meant to work and probably never will.

## What?
The aim is to generate new maps, tracks using NN's for a racing game called [TrackMania](https://www.trackmania.com/). I created this project a while ago for fun and mostly for educational purposes. [Medium post.](https://medium.com/@donadigo/tmtracknn-generating-trackmania-tracks-with-neural-networks-146db058e7cb)

## Generating new tracks
You can use `build.py` to generate new tracks and save them directly to a .Gbx file e.g:
```
python3 build.py -b models/block_model_300_300.h5 -p models/position_model_512_512_256.h5 -l 60 -c data/config.json -o GeneratedTrack.Challenge.Gbx
```
This will generate a track using the provided block and position models that will be 60 blocks in length and save the track to `GeneratedTrack.Challenge.Gbx`

## Dependencies
* Python 3
* Keras
* python-lzo (through pip)
* numpy
* Not required: pygame or Gtk+3 and GLib for track visualization

## Dataset
This repo doesn't contain the dataset itself used to train the models in the `models/` directory as it is unusual to provide entire datasets with code in one repo. There is however a preprocessed version of the dataset used in the `data/train_data.pkl` file that you can use for futher training.

The file contains roughly 3000 tech tracks downloaded directly from [TMX](https://tmnforever.tm-exchange.com/) and preprocessed such that they contain only the simplified version of tracks of each map. The maps themselves were downloaded using these filters: type: tech, order: awards (most), length: ~= 1m.

## Neural Network Architecture
We can represent a track as a sequence of block placements. Each block consists of 3 main features:
* block type (that is if it's a turn, a road, a tilted road etc.)
* it's position on the map (that is it's X, Y, Z coordinates)
* it's orientation / rotation (if it's facing north, west, south or east)

TMTrackNN at the moment uses 2 neural networks that are used to predict those features of a next block in the sequence. Both NN's are LSTM networks.

### Block model
The block model receives a sequence of previous block placements. Each previous placement contains a one-hot encoded block type. At the output the network simply predicts the block type to put next. The output's loss function is the softmax function.

### Position model
The position model receives a complete sequence information about previous block placements. The model is fed with an encoding of previous blocks. Each encoding consists of a one-hot encoded block type, normalized a X, Y, Z vector from previous block and finally a one-hot encoding of it's rotation.

Since we want to predict the next block in the sequence we ask the block model to predict the next block type. Then we ask the position model to predict the position of that block type by encoding it as a last time step in the sequence that is fed to the position model. Therefore the last block in the sequence consists only of the one-hot encoding of the block type and position and rotation vectors are filled with -1's.

The position model's output is two features: the vector to add to the position of last block to get a new position of the new block and the rotation of the new block.
Their loss function is mean squared error and softmax respectively.

![Visualization](/docs/TMTrackArch.png)

## Training
It is recommended to have a dedicated GPU for training the nets, otherwise training process will be very slow.

To train the block net with the trained model in the `models/` directory:
```sh
python3 -i train_blocks.py -g -l models/block_model_300_300.h5
```

To train the position net with the trained model in the `models/` directory:
```sh
python3 -i train_pos.py -g -l models/position_model_512_256_256.h5
```

Invoking either `train_blocks.py` or `train_pos.py` with the `-l` option will automatically 
use model checkpointing to save new models with the model filename that was loaded.

`livebuild.py` allows to dynamically generate tracks, it has a Gtk+3 UI to visualize how the track currently looks like. To fully evaluate model's performance, it's recommended to use `build.py` and see the tracks generated in the game itself.
