==================================
PLACE Data Tutorial (Incomplete)
==================================

.. highlight:: python

Introduction
-----------------

This guide provides an overview of data acquisition and storage in
:term:`PLACE`.

Data Storage
-----------------

At its core, PLACE is a data acquisition framework. To support this philosophy,
many data storage options were considered. Several data recording requirements
were identified.

The chosen data format should:

- support Python 3.5+
- adhere to a well-defined standard
- be available on most systems, using common libraries
- be easy to learn and use
- store data in :term:`binary format`, to support larger data sets
- provide support for :term:`metadata` accompanying each data set

Based on these requirements, it was decided that the binary NPY format found
the NumPy library was suited to all our requirements, with the exception of
metadata. Metadata is stored by PLACE into at test-based JSON file.

Each PLACE experiment produces a directory containing these two files. The
experiment data is contained within a binary NPY file, named ``data.npy``
and the metadata is contained in a JSON file named ``config.json``. This
document will cover how data is added to these files, how to write modules that
contribute to these files, and how to review the data stored within these
files after an experiment.

How PLACE Views Data
------------------------

Every experiment in PLACE is performed using a number of different modules, as
selected by the user.  In the current version of PLACE, each module runs
independently and is unaware of any other modules being used in the experiment.
This is a disadvantage, because modules cannot (easily) make use of data or
settings from other modules. However, this was an intentional decision, as it
allows modules to be added by anyone, without needed to know how any other
module (or PLACE itself) behaves.  In a future version of PLACE, it may be
possible to send messages between modules, but this feature has not been
planned as of April 2018.

PLACE runs experiments serially. This means that each module is assigned a
priority and PLACE moves down the priority queue, giving each module a chance
to run. When one module is finished, the next is started. When all modules have
completed, this is considered one update. Experiments can contain any number of
updates, depending on the needs of the experiment.

Stored data from PLACE reflects this serialized loop of data acquisition. PLACE
produces a `NumPy Record Array
<https://docs.scipy.org/doc/numpy-1.13.0/user/basics.rec.html#record-arrays>`__.
A record array is similar to a spreadsheet with column headings. Each PLACE
update can be thought of as a row on the spreadsheet. Each module can produce
one or more columns within the spreadsheet. Therefore, each cell of the
spreadsheet is therefore associated with one update and one insturment. During
the update, the instrument can write data of any NumPy size/shape into its assigned
cell, provided it uses the same size/shape during each update. For example,
oscilloscopes may record 2 channels, by 50 records, by 10,000 voltage values as
a 2x50x10000 array. This entire array can be put into one cell of the record
array. However, instruments are allowed multiple columns of data, so the same
data could be recorded into two cells, with 50x10000 arrays in each.

NumPy Data
----------------

Data that has been acquired during an experiment is stored into a binary NumPy
file.  During the experiment, individual files will be written containing the
data for each update.  Doing this ensures that some data is retained in the
event the program crashes or is somehow unable to complete. If the experiment
completes normally, these individual files are merged into one file containing
all the data for the experiment.

Since NPY files are stored in a binary format, they must be loaded using the
NumPy library. The following lines of code in Python are sufficient to load a
NumPy file into a variable named ``data``.

::

    import numpy

    with open('data.npy', 'rb') as data_file:
        data = numpy.load(data_file)

Now ``data`` contains the entire record array. Row data (for one PLACE update)
can be accessed using integer values.

::

    first_update = data[0]  # Python arrays are zero-indexed
    tenth_update = data[9]

Columns can be accessed using the column heading. Column headings are defined
by the Python side of the PLACE module, but convention is to use the Python
class name followed by a hyphen and a text description of the column. If you
don't know the names of the column headings, you can print the headings usting
``data.dtype.names``.

::

    oscilloscope_data = data['Oscilloscope-trace']
    pressure_data = data['Pressure-value']

You can combine the two methods to access any specific cell in the record
array.  This will give you access to whatever data type was saved by the PLACE
module into that cell. If you are unsure, the documentation for the module
should describe the types and shapes of any data it returns.

Most of the time, the following script should get you started accessing your
data.

::

    import numpy as np

    with open('data.npy', 'rb') as data_file:
        data = numpy.load(data_file)

    update = 7
    heading = 'MyInstrument-values'

    process_data(data[update][heading])  # you would write this function

You can easily use ``for`` loops to iterate through update values if needed.
For additional information, please refer to the `Python docs
<https://docs.python.org>__`.

Metadata
-----------------


=========================
To Be Continued...
=========================
