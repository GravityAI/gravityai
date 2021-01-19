# <a href="https://gravity-ai.com">Gravity-ai.com</a>

This package includes helper scripts for interfacing your machine learning code with the <a href="https://gravity-ai.com">Gravity-ai.com</a> containerization code.

To install from pypi:

```
pip install gravityai
```

To install from source:

```
python3 setup.py install
```

## Example Implementation Code

```
from gravityai import gravityai as grav

# the following function is a callback (defined by you), that may be
# async or synchronous and that may be called multiple times, to
# transform input data against an algorithm or model (or whatever you want)
# If an error is experienced, return an error string message, or throw an exception.
def process_data(dataPath, outPath):
    # TODO:
    # Read data in from dataPath
    # Transform Data via model
    # Write data out to outPath
    # Return None if everything went ok.
    # return an error string if there was a problem.


# TODO Initialize models, etc. before calling wait_for_requests.

grav.wait_for_requests(process_data)

```

## Building a new Version

To build a new version for pypi (only we do that):

```
python3 -m pip install --user --upgrade setuptools wheel

python3 -m pip install --user --upgrade twine

python3 setup.py sdist bdist_wheel

python3 -m twine upload --repository pypi dist/*
```

Use the saved credentials, and remember the username is \_\_token\_\_
