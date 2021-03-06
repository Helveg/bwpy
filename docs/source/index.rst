.. bwpy documentation master file, created by
   sphinx-quickstart on Wed Feb  3 17:57:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bwpy's documentation!
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

``bwpy`` helps you interact with `3Brain's <https://www.3brain.com/>`_ `BrainWave
<https://www.3brain.com/products/brainwave>`_ data formats BRW and BXR. It is built on top
of `h5py <https://www.h5py.org/>`_ as the data formats are contained within an HDF5
structure.

The package can be installed as follows:

.. code-block:: bash

   pip install bwpy

BWR and BXR files can be opened as a regular :class:`h5py.File` objects (see `File Objects
<https://docs.h5py.org/en/stable/high/file.html>`_):

.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      print(datafile.description)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
