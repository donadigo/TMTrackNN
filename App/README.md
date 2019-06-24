## Here you can find the C++ source for the Qt UI for Windows.

This version should / will likely have more features than `gui.py` as it is used for actual releases.

### Compiling
There's a lot of paths that are hard-coded in the VS project and I don't recommend trying to compile it in it's current state. You'll have to mirror all the paths that contain all the headers / libs.

The easiest way to compile the project is to open it in Visual Studio (2017) and build it from there. However you'll also need to configure data paths found in `QtGuiApplication1/Config.h` and build in debug mode, otherwise it won't work.


