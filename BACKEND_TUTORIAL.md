# PLACE Plugins: An Overview

PLACE is a system for controlling laboratory hardware to perform and
*Experiment*. The system is written to be as modular (and as simple) as
possible. Each hardware component is viewed as a *plugin* to the system.
Therefore, it is especially important that each plugin adhere to specific
guidelines. The document will provide a walkthrough for developing a new plugin
for PLACE.

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

Currently, these are three methods you must implement.

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

### config(self, metadata, total\_updates):
This method is called by PLACE at the beginning of the experiment. This is when
you should get everything up and running for the instrument.

As a convenience, the module is provided with the total number of updates (the
next method) that will be called for your module.

Additionally, you will receive a `metadata` dictionary This dictionary holds
values measured by devices at the start of an experiment. During the `config`
phase, you should add any values you would like to set for the entire
experiment. A common usage might be to record the serial number and calibration
data of the instrument you are using. **Please avoid common names, since the
dictionary is shared. Otherwise, you might clobber data and invalidate an
experiment.** The data recorded into the metadata dictionary will be saved into
the configuration data for the experiment, stored as `config.json` in the
experiment directory.

### update(self, update\_number)
This method is called by PLACE during the experiment. For example, one
experiment might take measurements from 100 different places on an object. This
means PLACE will call update on your method 100 times. Each time it is called,
you will need to do whatever it is your instrument needs to do during that
time. If your instrument is moving the object, this is when you do that. If you
are taking a measurement, then your instrument needs to do that. PLACE isn't
interested in what your instrument actually does, it's just telling you that
it's your turn.

You will also have access to the current update number, so your module can
easily keep track of how much of the experiment is remaining.

### cleanup(self, abort=False)
This method is called by PLACE at the end of the experiment. It may also be
called if there is a problem with the experiment. Unfortunately, there is no
guarantee that this method will be called, so do as much as possible to keep
resources as free as possible. If this does get called, though, your device
should assume the experiment has ended and the code should free all used
resources.

If the `abort` parameter is set, this indicates that the experiment is being
abandoned, perhaps due to a safety concern, such as a problem with one of the
instruments. In this case, halting all real world activity should be
prioritized, and tasks regarding plotting, software resources or data integrity
can be skipped.

# ... to be continued.
