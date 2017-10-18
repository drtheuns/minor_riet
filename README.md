# Measuring Heritage Emotions

This project uses Python, DLib, OpenCV and Facial Landmarks to recognize emotions from images/videos.

# Motivation

According to Waag Society and the Research Group Crossmedia, recent studies have shown that
young adults (<21) are hard to reach when it comes down to (cultural) heritage. In particular Waag
Society is researching how cultural heritage institutions can connect to these groups and how heritage
objects can be relevant to (young) people. Both parties believe that a better understanding of the
emotions people have, is very important to learn more about the way people value cultural heritage.
Therefore, Waag Society and the Research Group Crossmedia asked students of the HvA to design
an interactive tool that captures young adults’ emotions and enables them to discuss these emotions
with their peers when looking at (cultural) heritage.

# Getting Started

In order to get the program working, quite a number of prerequisites must be met. Most of these involve external libraries.

A lot of what is described here, can be read back in more detail on Paul van Gent's blog (see also [the citations](#citations)).

## Requirements

- Python 2.7
- Dlib (we used: dlib 19.7)
- Boost (we used: 1.65.1)
- SKLearn (`pip install sklearn`)
- Numpy (`pip install numpy`)
- OpenCV (we used: 2.4.13)

You might want to use a virtualenvironment when setting up everything below.

Building Dlib is fairly straightforward. You can read the details on this on Paul van Gent's blog, or you can google it. It basically requires the C++ Boost library to be build, and then you can build Dlib and install it for Python. If everything installed correctly, but you still get an `ImportError` when importing dlib, running `sudo ldconfig` might solve this. 

SKlearn will already be installed if you're using [Anaconda](https://www.anaconda.com/). If not, `pip install sklearn` will do the trick. `pip install numpy` is sufficient for numpy as well.

OpenCV gave a lot of trouble when building from source. So here are a couple of notes / tips that helped make the build succesful:
- If you want to build OpenCV version 2.4.9, you might run into an error during building pertaining to the `face_detector.cpp`, you should try building a newer version of OpenCV (2.4.13 for example).
- The build might fail on `ffmpeg`. In this case, you should build `ffmpeg` from source before building OpenCV. For example:
```bash
cd ffmpeg-<version>
./configure --enable-nonfree --enable-pic --enable-shared
make
sudo make install
```
**Warning** This will override any version of `ffmpeg` you might already have installed. Any software that relied on `ffmpeg` might break as a cause of this (ex. `mpv`).
- You might need to run `cmake` with `-D ENABLED_PRECOMPILED_HEADER=OFF` (see also [this github issue](https://github.com/opencv/opencv/issues/8878))

What worked for us eventually:

- Build `ffmpeg` from source.
- Next use `CMake`:
```bash
cd opencv-<version>
mkdir build
cd build
cmake -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLE=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=ON -D WITH_OPENGL=ON -D WITH_VTK=ON -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D ENABLE_PRECOMPILED_HEADERS=OFF -fPIC ..
```
- Check the output of `CMake` to ensure there is `ffmpeg` support.
- Make and make install: `make && make install`

Once the build is successful, check in a Python interpreter session that you can do `import cv2`. If this is not the case, you might need to manually copy or symlink `cv2.so` to your `python2.7/lib` folder:
```bash
cp /path/to/opencv/build/lib/cv2.so /path/to/virtualenv/lib/python2.7/cv2.so
OR to symlink:
ln -s /path/to/opencv/build/lib/cv2.so /path/to/virtualenv/lib/python2.7/cv2.so
```
Open a new Python interpreter session, and try `import cv2` again.

# Citations

- van Gent, P. (2016). Emotion Recognition Using Facial Landmarks, Python, DLib and OpenCV. A tech blog about fun things with Python and embedded electronics. Retrieved from: http://www.paulvangent.com/2016/08/05/emotion-recognition-using-facial-landmarks/


