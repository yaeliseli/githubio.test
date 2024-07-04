
Installation
============

Install Python
--------------

As DHTK is a Python modules, make sure you have Python installed on your
system. You can do this in three different ways:

1. Manually search the common locations where your system saves
    applications.
2. You can use the search file options from you system to find the
    Python application
3. You can type python --version on your command line or powershell
    (Windows)

If you don't have Python 3 installs, please [download
it](https://www.python.org/downloads/) and follow the instructions. We
recommend using the most up-to-date Python 3 version, but DHTK is
compatible with at least Python 3.7+.

Install Docker
--------------

In addition to Python 3, you are likely to use a local SPARQL endpoint
when using DHTK to search pre-processed data. This requires setting up a
Fuseki server container on the Docker application. To do so, you will
need to [download Docker](https://docs.docker.com/get-docker/) before
running DHTK.
---
 **note**

 DHTK may attempt to install docker (macOS systems only) and set up all
 required containers and volumes.
---
Install DHTK
------------

DHTK can be installed as a regular python modules, using the package
installer for Python (pip):

    $ pip install git+https://gitlab.com/dhtk/dhtk.git

Alternatively, you may download the [DHTK source
code](https://gitlab.com/dhtk/dhtk/tree/master) in your preferred
format. Once you extract the DHTK files from the archive, you can access
them via command line (or powershell).

    $ cd dhtk
    $
    $ python setup.py  # or
    $ pip install .

Install extensions
-------------------
DHTK Extensions can be installed as a regular python modules, using the package
installer for Python (pip):

    $ pip install git+https://gitlab.com/dhtk/dhtk-extensions/dhtk-extension-<name_extension>.git

where *<name_extension>* has to be replaced with the name of the extension you wish to install (i.e https://gitlab.com/dhtk/dhtk-extensions/dhtk-extension-gutenberg.git)

Alternatively, you may download the [DHTK source
code](https://gitlab.com/dhtk/dhtk-extensions/dhtk-extension-gutenberg/-/archive/master/dhtk-extension-gutenberg-master.zip) in your preferred
format. Once you extract the DHTK files from the archive, you can access
them via command line (or powershell).

    $ cd dhtk
    $
    $ python setup.py  # or
    $ pip install .
---
 **note**

 DHTK runs a number of system check to try to guarantee if can run
 without any problem. If this is the first time you're running it, keep
 in mind that it may take considerable time to complete the the full
 set.
---