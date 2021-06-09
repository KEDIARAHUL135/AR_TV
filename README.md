# AR_TV

This project is aims to create an effect of virtual Television on a wall. This projects a video on a wall over the 4 pasted Aruco Markers giving the effect of a TV.
Code is available in Python and C++.

You can find complete explaination of the logic and documentation of the code [here](https://www.scribd.com/document/510887777/Augmented-Reality-Television-with-Aruco-Markers).


### Installation

Clone this repository and follow the steps below to run the code.

##### Python
* Install the following dependencies.
    * `opencv-contrib-python`
    * `numpy`
* Set the path of the two input videos in the file `main.py` at the lines 55, and 58.
* Run the code using terminal
    * Navigate to the cwd.
    * Run: `$ python main.py`
    
#### C++
* Make sure you have OpenCV binaries installed.
* Set the path of the two input videos in the file `main.cpp` at the lines 91, and 92.
* Run the file `main.cpp`. For CMake users, `CMakeLists.txt` is also created.
