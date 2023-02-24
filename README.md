# python-xlab

Documentation can be found at the [Github Pages](https://demcon.github.io/python-xlab/)

## Install

You need **NI-VISA** in order to run `xlab`. Download it from: https://www.ni.com/nl-nl/support/downloads/drivers/download.ni-visa.html  
You can deselect all extra features to save a lot of disk space. You *do not* need to disable Windows Fast Startup when prompted.

Install xlab direclty using pip and Git:
```cmd
pip install git+https://github.com/DEMCON/python-xlab.git
```

All required packages are installed automatically.

### Develop

To run it from source, prepare a Python virtual environment with:

```cmd
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then make an editable install with:

```cmd
pip install -e .
```

## Compatibility

Both Python 3.8 and 3.10 were tested and seem to work.

``xlab`` was originally made for PySide1, but that is no longer available after Python 3.7.
Therefor PySide1 was ported to PySide2.

Later versions of ``pyvisa`` do not work!
