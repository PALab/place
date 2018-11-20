**********************************
PLACE Data Tutorial
**********************************

.. highlight:: python

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
metadata. Metadata is stored by PLACE into a text-based JSON file.

Each PLACE experiment produces a directory containing these two files. The
experiment data is contained within a binary NPY file, named ``data.npy``
and the metadata is contained in a JSON file named ``config.json``. This
document will cover how data is added to these files, how to write PLACE plugins that
contribute to these files, and how to review the data stored within these
files after an experiment.

How PLACE Views Data
=======================

Every experiment in PLACE is performed using a number of different plugins, as
selected by the user.  In the current version of PLACE, each plugin runs
independently and is unaware of any other plugin being used in the experiment.
This may be seen as a disadvantage, because plugins cannot (easily) make use of
data or settings from other plugins. However, this was an intentional decision,
as it allows plugins to be added by anyone, without needing to know how any
other plugin (or PLACE itself) behaves.  In a future version of PLACE, it may be
possible to send messages between plugins, but this feature has not been planned
as of November 2018.

PLACE runs experiments serially. This means that each plugin is assigned a
priority and PLACE moves down the priority queue, giving each plugin a chance to
run. When one plugin is finished, the next is started. When all plugins have
completed, this is considered one :term:`update`. Experiments can contain any
number of updates, depending on the needs of the experiment.

Stored data from PLACE reflects this serialized loop of data acquisition. PLACE
produces a `NumPy Record Array
<https://docs.scipy.org/doc/numpy/user/basics.rec.html#record-arrays>`__.
A record array is similar to a spreadsheet with column headings. Each PLACE
update can be thought of as a row on the spreadsheet. Each plugin can produce
one or more columns within the spreadsheet. Therefore, each cell of the
spreadsheet is associated with one update (the row number) and one insturment
(the column heading). During the update, the instrument can write data of any
NumPy size/shape into its assigned cell, provided it uses the same size/shape
during each update. For example, oscilloscopes may record 2 channels, by 50
records, by 10,000 voltage values as a 2x50x10000 array. This entire array can
be put into one cell of the record array. Alternatively, instruments are allowed
multiple columns of data, so the same data could be recorded into two cells,
with 50x10000 arrays in each.

Accessing Experimental Data
===============================

When you download a completed experiment from PLACE, it will contain a data
file, ``data.npy``, and a metadata/configuration file, ``config.json``.

**Note** - In rare cases where your experiment did not complete, you may find
several data files (instead of ``data.npy``), numbered ``data_000.npy``,
``data_001.npy``, etc. There will be one for each update that completed
successfully. You can combine these into one file using the ``place_pack``
command-line utility.

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

    import numpy as np

    with open('data.npy', 'rb') as data_file:
        data = np.load(data_file)

NumPy also supports this shortcut syntax:

::

    import numpy as np

    data = np.load('data.npy')

Now ``data`` contains the entire record array. Row data (for one PLACE update)
can be accessed using integer values.

::

    first_update = data[0]  # Python arrays are zero-indexed
    tenth_update = data[9]

Columns can be accessed using the column heading. Column headings are defined
in the Python module, but convention is to use the Python
class name followed by a hyphen and a text description of the column. If you
don't know the names of the column headings, you can print the headings usting
``data.dtype.names``.

::

    oscilloscope_data = data['Oscilloscope-trace']
    pressure_data = data['Pressure-value']

You can combine the two methods to access any specific cell in the record
array.  This will give you access to whatever data type was saved by the PLACE
plugin into that cell. If you are unsure, the documentation for the plugin
should describe the types and shapes of any data it returns.

Most of the time, the following script should get you started accessing your
data.

::

    import numpy as np

    with open('data.npy', 'rb') as data_file:
        data = np.load(data_file)

    update = 7
    heading = 'MyInstrument-values'
    cell_data = data[update][heading]

    process_data(cell_data)  # you would write the process_data() function

You can easily use ``for`` loops to iterate through update values if needed.
For additional information, please refer to the `Python docs
<https://docs.python.org>`_.

Metadata
----------------------

It was determined early on that metadata was an important part of the data
aquisition process in PLACE. The term :term:`metadata` is used to refer to all
the data describing a PLACE experiment.

In early versions of PLACE, data used to start an experiment was saved into a
file named ``config.json``. Metadata recorded about the experiment after the
experiment had already started was recorded into a file named ``metadata.json``.
These files were later merged into one file, after observing that many of the
configuration options are also useful metadata. Today, only ``config.json``
remains, and metadata recorded during an experiment is located under the
'metadata' key within this file.

Accessing JSON data is similar accessing NumPy data:

::

    import json

    with open('config.json') as json_data_file:
        json_data = json.load(json_data_file)

After loading the data from the file, you can easily access the settings of any
of the plugins used:

::

    name = 'Rocket'                # the plugin name
    setting = 'launch_trajectory'  # the configuration setting name

    trajectory = json_data['plugins'][name]['config'][setting]

Metadata recorded during the experiment is also available:

::

    key = 'vd_09_signal_delay'

    value = json_data['metadata'][key]

Other values are available, too, like the experiment title, comments, and
storage directory on the server. JSON files are fairly easy to read. Once you
locate the value you are looking for, JSON files are also very easy to use in
your Python scripts. And by using PLACE, you will ensure consistency across
experiments, so the settings you need will always be in the same location.

Writing Plugins that Store Data
========================================

If you are writing PLACE plugins, you will eventually run into one that needs to
save data for the user (beyond just the configuration values). PLACE focuses on
the *user experience* rather than the *developer experience*, so PLACE attempts
to store data in a way that is easiest for the user. So, while every effort is
made to also make things easy for the developer, this is not done at the cost of
the user.

With that in mind, this section will attempt to simplify the process of writing
plugins that save data that will be easy for the user to access.

Saving NumPy Data
-------------------------

From your plugin's perspective, PLACE data (not metadata) is saved during the
:term:`update phase` of an experiment. Remember, the update phase occurs one or
more times in every experiment.

It helps to think of the PLACE experimental data as a spreadsheet. The row
numbers are the update phases of the experiment. Over the course of the
experiment, your plugin can create one or more columns of data in this
spreadsheet. To do this, you will need to decide how many columns of data you
need, what their headings will be, and what will be recorded into each of your
*cells* during each update phase.

As and example, let's say I'm writing a plugin for a temperature probe. And
let's say this probe has 4 individual sensors (perhaps for different locations
on a sample). I might decide that I want my plugin to create a single column of
data called "temperature", and during each update I will record the temperature
reading from each sensor, as an array, into the *cell* of the PLACE NumPy data
array.

So, that sounds like a good plan, but how do I put this into my plugin code?

As mentioned, everything will happen during the update phase, so our code will
be in the ``update()`` method of our plugin (or in a function called from this
method).

First, we need to read the data from our imaginary temperature probe. We'll just
assume we have a function that does that.

::

    temp1 = read_from_probe(1)
    temp2 = read_from_probe(2)
    temp3 = read_from_probe(3)
    temp4 = read_from_probe(4)
    data = [temp1, temp2, temp3, temp4]

Next, we need to construct the string to use as our column heading. We actually
have to specify this for every update because PLACE saves each update as a
separate file and merges them into one only at the very end of the experiment.
It is important that we try to make a unique column heading, or else another
plugin could overwrite our column with its own data. Typically, just putting the
instrument class name in the column name will work.

::

    heading = self.__class__.__name__ + '-temperature'

The next step is to tell PLACE about the data we are putting into our cell.
NumPy requires that our data be the same size (number of bytes) for each update.
So by telling NumPy the size of our data up front, it will tell us (via an
error) if we break the rules.

*This next step is the most* computer-science-y *of them all, so looking at
examples in other plugins or reading about it online might be useful. Here we
go.*

To tell NumPy about our data, we need to construct a NumPy ``dtype`` object.
Basically, this is just a specific way of saying if you are storing integers or
decimals, and how many you are storing. There is a lot of information about this
on the `NumPy site
<https://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html>`_.

First we will select the correct numerical data type for our data. Here is `a
list of NumPy numerical data types
<https://docs.scipy.org/doc/numpy/user/basics.types.html>`_. Whenever possible,
using one these types is preferred to the generic Python types. Most of the
time, using ``int64`` or ``float64`` is probably fine. We will assume our
temperature data is a decimal number, so we will use ``float64``.

Now, if we only had one temperature to store, we would be ready to create our
``dtype``. It would look like this:

::

    dtype = np.dtype([(heading, np.float64)])

    # The square brackets are required. If you were creating multiple columns of
    # data, you would just add the next one inside the same square brackets.
    # dtype = np.dtype([(heading1, np.float64), (heading2, np.int64)])

When we are store multiple values into each cell, we must specify the NumPy
shape of the data. This can be an integer value, or a tuple (for
multi-dimensional data). We have 4 values, so we will just use 4.

::

    dtype = np.dtype([(heading, np.float64, 4)])

Excellent. Now we should have everything we need to create our data entry for
PLACE. It all goes together like this:

::

    record = np.array([(data,)], dtype=dtype)

    # The comma after data is required when you only have one column of data.
    # With two or more columns, it is not.
    # record = np.array([(data1, data2)], dtype=dtype)

To finish recording our data, we just return it to PLACE at the end of the
``update()`` method. Here is how it all looks together:

::

    temp1 = read_from_probe(1)
    temp2 = read_from_probe(2)
    temp3 = read_from_probe(3)
    temp4 = read_from_probe(4)
    data = [temp1, temp2, temp3, temp4]

    heading = self.__class__.__name__ + '-temperature'
    dtype = np.dtype([(heading, np.float64)])
    record = np.array([(data,)], dtype=dtype)

    return record

And, for convenience, here is how the user would extract the temperature reading
from probe sensor 3 from update 12 (assuming the plugin name is Probe):

::

    import numpy as np

    data = np.load('data.npy')
    update = 11  # 0-indexed
    sensor = 2   # also 0-indexed
    update_12_probe_3_temp = data['Probe-temperature'][update][sensor]

Saving JSON Metadata
-------------------------

Compared to NumPy data, saving metadata is super easy! Metadata is saved during the :term:`config phase` only,
because metadata should not depend on any measurements taken during the update phase. So, if you think you
have metadata that **does** depend on the measurements, it is probably actually just another experimental measurement,
and should be put into the NumPy data.

At the moment, metadata is only differentiated by its key, so it's important to make sure and store it
under a unique key. As with the NumPy headings, placing your plugin class name in the key is a pretty good way
to make something that is unique (although this isn't currently the *official* best practice).

Using the temperature probe from the previous section as an example, perhaps we have two different probe models which both
use the same PLACE plugin. During the config phase, it would be good to read the model number and store it into the metadata.
We will assume ``read_model_number()`` is a Python function written elsewhere.

::

    key = self.__class__.__name__ + '-model-number'
    metadata[key] = read_model_number()

So, obviously pretty simple, right? And then, for a user to read this data, or use it in script, they would do something like this:

::

    import json

    with open('config.json') as json_data_file:
        json_data = json.load(json_data_file)

    model = json_data['metadata']['Probe-model-number']

PLACE Data User Experience Summary
=======================================

As mentioned, PLACE is designed to provide a good user experience, while still being flexible.
The following code shows how users can expect to consistently access PLACE experimental data.

::

    import json
    import numpy as np

    with open('config.json', 'r') as json_data_file:
        config = json.load(json_data_file)

    with open('data.npy', 'rb') as npy_data_file:
        data = np.load(npy_data_file)

    model = config['metadata']['Probe-model-number']
    print('Probe {} summary'.format(model))
    for update, (t1, t2, t3, t4) in enumerate(data['Probe-temperature']):
        print('Update {}: {}, {}, {}, {}'.format(update, t1, t2, t3, t4))

