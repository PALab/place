# PLACE Plugins: An Overview

PLACE is a system for automating hardware devices to accomplish a *Scan*. The system is written to be as modular (and as simple) as possible. Each hardware component is viewed as a *plugin* to the system. Therefore, it is especially important that each plugin adhere to specific guidelines. The document will provide a walkthrough for developing a new plugin for PLACE.

## Plugin files

Writing your own plugin for PLACE means supplying a few files that PLACE will look for when it is running. Essentially, this includes a Python module and a JavaScript script. However, as you will see, this may also include an Elm file and a Python test file. Your specific plugin may require additional files, which is totally allowed.

Here is a breakdown of the how the plugin files you write fit into the directory structure of PLACE.

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
This contains documentation for PLACE. Currently, we autogenerate documentation using [Sphinx](http://www.sphinx-doc.org/en/stable/), so you do not need to create anything for this directory, you just need to properly document your Python code.

### The *elm* directory
This contains Elm source. Elm is a programming language designed to generate JavaScript. It is **highly** recommended if you are writing plugins for PLACE, but it is not required. PLACE will not look at anything in this directory. *Note that Elm files enforce a slightly different naming convention.*

### The *place* directory
This is the Python module for PLACE. So, this is where everything happens. There is a subdirectory named *plugins*. Your Python module for you plugin goes here. The name of this directory is the semi-official name of your plugin, so make sure you give it a logical name.

Inside this directory is an `__init__.py` file. This file should import anything that you want available to PLACE. Typically, this will be the instrument classes you write. So, typically, a single line, like `from .new_plugin import InstrumentA, InstrumentB` is all that's needed.

Your Python files can really be named anything you like, but generally the entry point file should have the same name as your plugin - up to you. Remember that the `__init__` file will take care of exposing stuff to PLACE, so it's really no big deal what names you use.

Any test files you write should be in a file that starts with `test_`. The `unittest` library in Python will be called on your plugin in discovery mode when PLACE is built, so make sure all your unittests are passing or PLACE won't build.

### The *web* directory 
This contains the code for executing the web interface for PLACE. Your plugin should include a web interface, but if you write it in Elm, we will build this file automatically. This guide will not cover how to use JavaScript to write a web interface.

## Instrument interface
In `place/place/plugins` you will find a Python file containing an Instrument interface class. An *interface* is essentially a class that names methods that must be implemented by subclasses. By making your plugin classes a subclass of `Instrument` you will ensure that you have implemented all the required methods used by PLACE during a scan. Start your instrument classes like this:

    from place.plugins.instrument import Instrument
    class MyDevice(Instrument):
        # (definition goes here) #

Currently, these are the methods you must implement.

### __init__(self, config)
This is the standard constructor for Python. We are passed the configuration data for our instrument, which should be a Python dictionary. PLACE will just take it from the web interface and send it to your code - simple as that!

As a subclass, we should ensure that the initializer of the base class is called. There are [a number of ways to do this](https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods) in Python, but using the explicit call to the initializer works fine, I think. Just call it like this:

    Instrument.__init__(self, config)

The Instrument initializer doesn't do anything other than save the configuration data into `self._config` and set `self.priority` to 100. This is done in the Instrument initializer because we need to ensure that these two things are there for PLACE. All the other class (self) variables can be determined as you see fit.

### config(self, header=None)
This method is called by PLACE at the beginning of a scan. This is when you should get everything up and running for the instrument.

Additionally, you will receive an `obspy.core.trace.Stats` object. This object is essentially a dictionary with a few enforced values. You can [read about it here](https://docs.obspy.org/packages/autogen/obspy.core.trace.Stats.html#obspy.core.trace.Stats). This dictionary holds values that describe the scan. During the `config` phase, you should add any values you would like to set for the entire scan. A common usage might be to record the serial number and calibration data of the instrument you are using. **Please avoid common names, since the dictionary is shared. Otherwise, you might clobber data and invalidate a scan.**

### update(self, header=None, socket=None)
This method is called by PLACE during a scan. For example, one experiment might take measurements from 100 different places on an object. This means PLACE will call update on your method 100 times. Each time it is called, you will need to do whatever it is your instrument needs to do during that time. If your instrument is moving the object, this is when you do that. If you are taking a measurement, then your instrument needs to do that. PLACE isn't interested in what your instrument actually does, it's just telling you that it's your turn.

As with the config stage, you will receive the `Stats` object. During the update phase, you might record the measurement taken by your instrument. Or maybe you record the current position of your instrument. Just make sure you are *updating* values during the *update* phase, and not trying to add new values into the dictionary with each update.

If PLACE is being run form the web interface, you will receive a websocket object. This socket directly links back to an HTML iframe in the web interface. You can send HTML data into this socket if you wish, but keep in mind that only one instrument should use this per scan or you may end up with the display flipping between the display of multiple instruments, as each tries to show its data.

### cleanup(self)
This method is called by PLACE at the end of the scan. It may also be called if there is a problem with the scan. Unfortunately, there is no guarantee that this method will be called, so do as much as possible to keep resources as free as possible. If this does get called, though, your device to assume it is done with the scan, and the code should free all used resources.

This method can return a NumPy array, which will be written into the HDF5 file of scan data.

# Example: Movement stage
In this example, we will write a plugin for an XPS-C8 controller that moves a stage during a scan.

## Create xps_control Python module
First, we create a directory in `place/place/plugins` called `xps_control`. This instrument already provides a Python driver, named `XPS_C8_drivers.py`, so this will be the first file in our new Python module. However, since this is a proprietary driver, we will write our code in a different Python file and just make calls into the driver as necessary.

### Writing the xps_control code
We create a new file, named `xps_control.py`. Note that it matches our module name. This is not required, but is good if you don't have a different name in mind.

Let's start with some basic instrument code. We know we will be sub-classing the Instrument interface, so we actually have a lot of code to write already. It starts like this:

    """Stage movement using the XPS-C8 controller"""
    from place.plugins.instrument import Instrument
    
    class Stage(Instrument):
        """Basic stage instrument"""
        def config(self, json_string):
            """setup for a scan
            
            :param json_string: JSON-formatted configuration
            :type json_string: str
            """
            pass
            
        def update(self):
            """move the stage"""
            pass
            
        def cleanup(self):
            """end of scan"""
            pass

*Please notice how I've already started documenting my code, using the Sphinx style as appropriate. Throughout this guide, I will often leave out docstrings and other unnecessary stuff. I will use `# ... #` to indicate that I am omitting some code. This way, I can focus on the task at hand. Please don't interpret this as meaning that the details aren't important.*

Looking at this code, it actually seems relatively simple. We just have to write three methods and we are done! In many ways, it's as easy as that.

Let's start with the `update(self)` method. When this is called, we should move the stage a certain distance. The XPS driver includes a command, `GroupMoveAbsolute`, that will move the stage.

# ... to be continued.
