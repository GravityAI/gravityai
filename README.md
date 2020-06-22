# Gravity-ai.com

This package includes helper scripts for interfacing your machine learning code with the Gravity-ai.com containerization code.

To install from pypi:

```
pip install gravityai
```

To install from source:

```
python3 setup.py install
```

To build a new version for pypi (only we do that):

```
python3 -m pip install --user --upgrade setuptools wheel

python3 -m pip install --user --upgrade twine

python3 setup.py sdist bdist_wheel

python3 -m twine upload --repository pypi dist/*
```

Use the saved credentials, and remember the username is \_\_token\_\_
