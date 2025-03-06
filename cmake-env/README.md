

# Application Description

Use this section to describe your application.

The template app doesn't send any useful data, but provides a starting point to develop your own apps. 
This app is written in C++ and uses the Qt framework.

The important source files are listed below:

- `main.cpp` is the entry point
- `mainwindow.cpp` contains the UI code and code to access the recording device
- `mainwindow.hpp` is the corresponding header

# Build

This application can be built following general
[LSL Application build instructions](https://labstreaminglayer.readthedocs.io/dev/app_build.html).

After cloning, run the following code on the command line (in a Ubuntu virtual environment):

```
cmake -S . -B build -DCMAKE_PREFIX_PATH="/mnt/c/path/to/repo/cabcs_lsl/5.15.2/msvc2019_64/lib/cmake/Qt5"
```

# License

Starting point provided by [MIT](https://choosealicense.com/licenses/mit/) license.

