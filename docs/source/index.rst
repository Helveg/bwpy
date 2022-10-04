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
The package allows slicing data of files of `.brw` format.  
Slices are masks that can be applied to the data.

Temporal slices can be obtained by calling the property `t`, which is an unidimensional `numpy` array:
.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      datafile.t[0:10:2]
      #will return the slice of the first 10 temporal recordings with a step of 2

Channel slices can be obtained by calling the porperty `ch`, which is bi-dimensional `numpy` array:
.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      datafile.ch[0:10, 0: 10]
      #will return the slice of the block of the first 10x10 channels

Slices can be combined:
.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      datafile.t[0:10].ch[0, 0]
      #will return the slice of the first 10 temporal recordings of the first channel

When the slicing is completed, it is possible to apply the mask to the data by calling `data` as it follows:
.. code-block:: python

   import bwpy

   with bwpy("my_data.bwr", "r") as datafile:
      sliced_data = datafile.t[0:10].ch[0, 0].data

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
