## Tools used for distribution.
These are tools used to:
* convert a Keras model to a protobuf 
* convert pattern data to a JSON file for the C++ version to read these.
* generate a C++ blocks array source

The release version uses a C++ Tensorflow header & DLL from [here](https://github.com/fo40225/tensorflow-windows-wheel/blob/master/1.8.0/cpp/libtensorflow-cpu-windows-x86_64-1.8.0-sse2.7z).
