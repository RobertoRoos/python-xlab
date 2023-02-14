# python-xlab

Documentation can be found at the [Github Pages](https://demcon.github.io/python-xlab/)

## Install

You need NI-VISA in order to run `xlab`. Download it from: https://www.ni.com/nl-nl/support/downloads/drivers/download.ni-visa.html  
You can deselect all extra features to save a lot of disk space. You *do not* need to disable Windows Fast Startup when prompted.

To run it from source, prepare a Python virtual environment with:

```cmd
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Alternatively, install the source (into a venv or a system install) as a package with:

```cmd
pip install [path\to\repo]
```
