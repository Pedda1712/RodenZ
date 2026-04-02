# RodenZ Code
The code is organized into two categories:
- `Libraries`, contains python packages with shared code
- `Tools`, the actual scripts the end user is supposed to run to configure parameters, infer 3D trajectories, etc..


## Installation
IMPORTANT: the code is NOT meant to be run with a python interpreter from the tools' source folders. 

Instead, build and install the code using the following procedure:
- Run `bash build.sh` from within this directory
- Create a python 3.12 (or higher) virtual environment, that you will use for your project, and install the `.whl` files: `pip install build/*.whl`

## For Developing
If you want to change code in the libraries/tools, create a python3.12 virtual environment and run `dev.sh` to install the packages as editable into your development environment. You can now use the packages in your own scripts, and any changes you make to package code will be reflected in your virtual environment.
