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

Slicing
-------

The package allows you to slice the data in `.brw` files. The data can be restricted to certain time samples by indexing the `.t` property like a one-dimensional array:
.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      # Return the slice of the first 10 temporal recordings with a step of 2
      datafile.t[0:10:2]

The data can be restricted to certain channels by indexing the `.ch` property like a two-dimensional array:

.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      # Return the slice of the block of the first 10x10 channels
      datafile.ch[0:10, 0: 10]

The obtained slices can themselves be sliced further:

.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      # Return the slice of the first 10 temporal recordings of the first channel
      datafile.t[0:10].ch[0, 0]

After slicing, the sliced data can be obtained by accessing the `data` property:

.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      sliced_data = datafile.t[0:10].ch[0, 0].data

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
