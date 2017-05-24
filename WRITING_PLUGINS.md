# PLACE Plugins: An Overview

PLACE is a system for automating hardware devices to accomplish a *Scan*. The
system is written to be as modular (and as simple) as possible. Each hardware
component is viewed as a *plugin* to the system. Therefore, it is especially
important that each plugin adhere to specific guidelines. The document will
provide a walkthrough for developing a new plugin for PLACE.

## Plugin files

Writing your own plugin for PLACE means supplying a few files that PLACE will
look for when it is running. Essentially, this includes a Python module and a
JavaScript script. However, as you will see, this may also include an Elm file
and a Python test file. Your specific plugin may require additional files,
which is totally allowed.

Here is a breakdown of the how the plugin files you write fit into the
directory structure of PLACE.

    place
    |-- docs
    |-- elm
    |   `-- plugins
    |       `-- NewPlugin.elm
    |-- place
    |   `-- plugins
    |       `-- new_plugin
    |           |-- __init__.py
    |           |-- new_plugin.py
    |           `-- test_new_plugin.py
    `-- web
        `-- plugins
            `-- new_plugin.js

I'll quickly explain this directory structure.

### The *docs* directory
This contains documentation for PLACE. Currently, we autogenerate documentation
using [Sphinx](http://www.sphinx-doc.org/en/stable/), so you do not need to
create anything for this directory, you just need to properly document your
Python code.

### The *elm* directory
This contains Elm source. Elm is a programming language designed to generate
JavaScript. It is **highly** recommended if you are writing plugins for PLACE,
but it is not required. PLACE will not look at anything in this directory.
*Note that Elm files enforce a slightly different naming convention.*

### The *place* directory
This is the Python module for PLACE. So, this is where everything happens.
There is a subdirectory named *plugins*. Your Python module for you plugin goes
here. The name of this directory is the semi-official name of your plugin, so
make sure you give it a logical name.

Inside this directory is an `__init__.py` file. This file should import
anything that you want available to PLACE. Typically, this will be the
instrument classes you write. So, typically, a single line, like `from
.new_plugin import InstrumentA, InstrumentB` is all that's needed.

Your Python files can really be named anything you like, but generally the
entry point file should have the same name as your plugin - up to you. Remember
that the `__init__` file will take care of exposing stuff to PLACE, so it's
really no big deal what names you use.

Any test files you write should be in a file that starts with `test_`. The
`unittest` library in Python will be called on your plugin in discovery mode
when PLACE is built, so make sure all your unittests are passing or PLACE won't
build.

### The *web* directory 
This contains the code for executing the web interface for PLACE. Your plugin
should include a web interface, but if you write it in Elm, we will build this
file automatically. This guide will not cover how to use JavaScript to write a
web interface.

## Instrument interface
In `place/place/plugins` you will find a Python file containing an Instrument
interface class. An *interface* is essentially a class that names methods that
must be implemented by subclasses. By making your plugin classes a subclass of
`Instrument` you will ensure that you have implemented all the required methods
used by PLACE during a scan. Start your instrument classes like this:

    from place.plugins.instrument import Instrument
    class MyDevice(Instrument):
        # (definition goes here) #

Currently, these are the methods you must implement.

### __init__(self, config)
This is the standard constructor for Python. We are passed the configuration
data for our instrument, which should be a Python dictionary. PLACE will just
take it from the web interface and send it to your code - simple as that!

As a subclass, we should ensure that the initializer of the base class is
called. There are [a number of ways to do
this](https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods)
in Python, but using the explicit call to the initializer works fine, I think.
Just call it like this:

    Instrument.__init__(self, config)

The Instrument initializer doesn't do anything other than save the
configuration data into `self._config` and set `self.priority` to 100. This is
done in the Instrument initializer because we need to ensure that these two
things are there for PLACE. All the other class (self) variables can be
determined as you see fit.

### config(self, header=None)
This method is called by PLACE at the beginning of a scan. This is when you
should get everything up and running for the instrument.

Additionally, you will receive an `obspy.core.trace.Stats` object. This object
is essentially a dictionary with a few enforced values. You can [read about it
here](https://docs.obspy.org/packages/autogen/obspy.core.trace.Stats.html#obspy.core.trace.Stats).
This dictionary holds values that describe the scan. During the `config` phase,
you should add any values you would like to set for the entire scan. A common
usage might be to record the serial number and calibration data of the
instrument you are using. **Please avoid common names, since the dictionary is
shared. Otherwise, you might clobber data and invalidate a scan.**

### update(self, header=None, socket=None)
This method is called by PLACE during a scan. For example, one experiment might
take measurements from 100 different places on an object. This means PLACE will
call update on your method 100 times. Each time it is called, you will need to
do whatever it is your instrument needs to do during that time. If your
instrument is moving the object, this is when you do that. If you are taking a
measurement, then your instrument needs to do that. PLACE isn't interested in
what your instrument actually does, it's just telling you that it's your turn.

As with the config stage, you will receive the `Stats` object. During the
update phase, you might record the measurement taken by your instrument. Or
maybe you record the current position of your instrument. Just make sure you
are *updating* values during the *update* phase, and not trying to add new
values into the dictionary with each update.

If PLACE is being run form the web interface, you will receive a websocket
object. This socket directly links back to an HTML iframe in the web interface.
You can send HTML data into this socket if you wish, but keep in mind that only
one instrument should use this per scan or you may end up with the display
flipping between the display of multiple instruments, as each tries to show its
data.

### cleanup(self)
This method is called by PLACE at the end of the scan. It may also be called if
there is a problem with the scan. Unfortunately, there is no guarantee that
this method will be called, so do as much as possible to keep resources as free
as possible. If this does get called, though, your device to assume it is done
with the scan, and the code should free all used resources.

This method can return a NumPy array, which will be written into the HDF5 file
of scan data.

# Example: Software Counter
In this section, we will write a plugin for an simple software counter that
keeps count of thenumber of updates, produces some sample data, and performs a
configurable sleep. This is intended to demonstrate the process of writing a
plugin without getting bogged down in code.

This example module exists in PLACE and has been thoroughly commented. Feel
free to refer to it as you read through this guide.

## Step 1: The Python plugin module
We create a directory in `place/place/plugins` called `counter`. This is our
*module name*. In this directory, we create `__init__.py` and `counter.py`, and
`test_counter.py`.

### Module initialization
This file exports the classes we write into the counter module. This must be
done or PLACE will not find our classes. Most instruments will have an
`__init__.py` file that looks like this:

    """Counter instrument class"""
    from .counter import Counter

It is important not to forget that `__init__.py` is a regular Python file, and
should therefore have appropriate docstrings, etc.

### Module source
This is where we will put our code for this instrument. For more complicated
instruments, this can be split into an arbitray number of files, as long as the
`__init__.py` file exports the classes, how you write them is up to you.

As we talk about the module source code, I will omit discussing the imports and
docstrings. Both can be referenced in the [counter.py
file](https://github.com/PALab/place/blob/master/place/plugins/counter/counter.py),
available in this repository.

#### Subclass the Instrument class
All instruments need to be subclassed from the PLACE Instrument class. PLACE
will actually check this, and even though your class might work perfectly fine
without being a subclass, PLACE still won't run it. So, start each instrument
like this:

    class Counter(Instrument):

#### Write the constructor method
Python classes are constructed using the `__init__` method. In this method, you
will call the Instrument constructor and document any class variables you will
be using.

    def __init__(self, config):
        Instrument.__init__(self, config)
        self._count = None
        self._stream = None

Our counter class keeps track of the count, obviously. It also keeps a variable
named `self._stream` that will hold an [ObsPy Stream
object](https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.html)
with some dummy data, just so we can demonstrate plotting and saving data. All
the variables are set to `None` at the moment, so think of this as just a list
of variables our class needs.

#### Write the config method
If the config method is called, this means that the scan will soon begin and we
should prepare. Now we can put values to the variables and get things started.

    def config(self, header=Stats()):
        self._count = 0
        self._stream = Stream()
        header['counter_sleep_time'] = self._config['sleep_time']

We start the counter at 0, because there have been 0 updates called so far.
`self._stream` is initialized to the empty
[Stream](https://docs.obspy.org/packages/autogen/obspy.core.stream.Stream.html).
After initializing our two class variables, we store the sleep time into the
header metadata. The sleep time is stored in `self._config` because it is a
user specified value. The Instrument initializer put all the user configuration
data into `self._config`, so anytime we need one of these values, this is where
we look for it. The sleep time is stored into the header so that it is written
into the HDF5 file at the end of the scan, this way there is a permanent record
of it bundled with the data. We record it into the metadata during the config
phase, because it will remain the same for the duration of the scan.

#### Write the update method
When this has called, the scan has started and it is our instrument's turn to
update.

    def update(self, header=Stats(), socket=None):
        self._count += 1
        header['counter_current_count'] = self._count
        some_data = np.random.rand(self._count)
        self._stream.append(Trace(some_data, header))
        if self._config['plot']:
            if not socket:
                plt.ion()
                plt.clf()
                plt.plot(some_data)
                plt.pause(0.05)
            else:
                plt.clf()
                plt.plot(some_data)
                out = mpld3.fig_to_html(plt.gcf())
                thread = Thread(target=send_data_thread, args=(socket, out))
                thread.start()
                thread.join()
        sleep(self._config['sleep_time'])

Okay, there is a bit more happening here, but it isn't too bad once we start
breaking it down. First we increment the count and store the current count into
the header metadata. This way, all the instruments will have the count data
attached to their header.

Next, we generate a random array, a append it to an ObsPy Stream.

Then we check if the user configuration specified a plot. If so, then we have
two cases: either we have a socket connecting to the web interface, or we
don't. If we don't, we just plot it using matplotlib and it should appear in a
new window. But if we do have a socket, then we convert that same plot to HTML
and send it out over the socket. Sending over the websocket is a coroutine, so
we perform it in a new thread, but we wait for it to finish before moving on.

Finally, we perform the sleep, as specified in the configuration data.

One thing you may have noticed is the new function that snuck in there. It was
called `send_data_thread`. This is the function that sends the data to the web
interface, and it is written in the file that hold the Instrument class. Just
import it and you can use it for any instrument.

#### Write the cleanup method
The cleanup method gives us a chance to free any resources used by our
instrument and return a NumPy array for output to the scan's HDF5 file.

    def cleanup(self):
        if self._config['plot'] == 'yes':
            plt.close('all')
        return self._stream

This is pretty simple. If we plotted anything, then we close all those figures.
It may not be necessary to do this, but it won't hurt. Then we return the data
we've been saving in our stream, mostly to test file output functionality in
PLACE.

# ... to be continued.
