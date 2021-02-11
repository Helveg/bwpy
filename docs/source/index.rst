.. bwpy documentation master file, created by
   sphinx-quickstart on Wed Feb  3 17:57:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://codecov.io/gh/Helveg/bwpy/branch/main/graph/badge.svg?token=OB8U3U8AFW
   :target: https://codecov.io/gh/Helveg/bwpy

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. image:: https://github.com/Helveg/bwpy/workflows/Build%20and%20test%20bwpy/badge.svg
   :target: https://github.com/Helveg/bwpy/actions

Welcome to bwpy's documentation!
================================

``bwpy`` helps you interact with `3Brain's <https://www.3brain.com/>`_ `BrainWave
<https://www.3brain.com/products/brainwave>`_ data formats BRW and BXR. It is built on top
of `h5py <https://www.h5py.org/>`_ as the data formats are contained within an HDF5
structure.

The package can be installed as follows:

.. code-block:: bash

   pip install bwpy

BWR and BXR files can be opened as a regular :class:`h5py.File` objects (see `File Objects
<https://docs.h5py.org/en/stable/high/file.html>`_), on top of that many of the metadata
is available as properties:

.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      print(datafile.description)
      print(datafile.version)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   bwpy

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
