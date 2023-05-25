**************************************
Python Backend Tutorial
**************************************

Overview
====================

:term:`PLACE` is a system for controlling laboratory hardware to perform an
:term:`experiment`. The system is written to be as modular (and as simple) as
possible. Each hardware component is viewed as a :term:`plugin` to the system.
Therefore, it is especially important that each plugin adhere to specific
guidelines.

To reach a wide audience, the PLACE backend is written entirely in
Python. Python is a highly accessible language. Python is also robust
and has a wide range of libraries used by the scientific community.

This document will provide a walkthrough for developing a new plugin for
PLACE.

Before you begin
----------------------

If you have never written a plugin for PLACE, and you want to begin
using a new piece of hardware in your experimental setup, it is highly
recommended that you learn to use the new hardware independently of
PLACE before you begin writing your PLACE plugin. Remember that at its
core, PLACE is automation software and does not replace the need for
drivers for your instrument.

If you already know how to control your hardware using the Python
interpreter, or by writing short Python scripts, this will make it very
easy to write your PLACE plugin.

Necessary files
------------------------

When PLACE runs your plugin, it must be given the Python module name and the
Python class name. With these two pieces of information, it will then attempt to
perform, essentially, the following code:

::

    from place.plugins.<module_name> import <class_name>
    <class_name>.config()
    for i in range(update_number):
        <class_name>.update()
    <class_name>.cleanup()

This is the directory structure for the PLACE source code:

::

    place
    |-- elm
    |   `-- plugins
    |       `-- helpers
    |-- place
    |   `-- plugins
    |-- placeweb
    |   |-- static
    |   |   `-- placeweb
    |   |       |-- documentation
    |   |       `-- plugins
    |   `-- templates
    |       `-- placeweb
    `-- sphinx

I'll quickly explain this directory structure.

The *elm* directory
^^^^^^^^^^^^^^^^^^^^^^^^^^

This contains Elm source. Elm is a programming language designed to
generate JavaScript. Elm is **highly** recommended if you are writing
modules for PLACE, but it is not required. PLACE will not look at
anything in this directory. *Note that Elm files enforce a slightly
different naming convention.*

The *place* directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the Python backend for PLACE. So, this is where lots of things happen.
There is a subdirectory named *plugins*. Your PLACE backend module goes here.
The name of this directory is the semi-official name of your plugin, so make
sure you give it a logical name.

Inside this directory is an ``__init__.py`` file. This file should
import anything that you want available to PLACE. Typically, this will
be the instrument classes you write. So, typically, a single line, like
``from .new_plugin import InstrumentA, InstrumentB`` is all that's
needed.

Your Python files can really be named anything you like, but generally
the entry point file should have the same name as your plugin - up to
you. Remember that the ``__init__`` file will take care of exposing
stuff to PLACE, so it's really no big deal what names you use.

Additionally, many modules require a Python driver either provided by
the manufacturer or custom written. Files like this should be included
with your PLACE module, as well.

The *placeweb* directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This contains the code for executing the web interface for PLACE. Your module
should include a web interface, but if you write it in Elm, we will build this
file automatically. Using JavaScript to build PLACE interfaces is not
recommended nor supported.

The documentation built by Sphinx will also be put into the directory.

The *sphinx* directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This contains the Sphinx build files, which are basically ``.rst`` files
that instruct Sphinx how to build the webpages that contain the PLACE
documentation. Your Python source code should contain Sphinx markup in
the docstrings and you will eventually need to add a file in here for
your module, but we will ignore this for now.

Instrument interface
--------------------------

In ``place/place/plugins`` you will find a Python file containing an
Instrument interface class. An *interface* is essentially a class that
names methods that must be implemented by subclasses. By making your
plugin classes a subclass of ``Instrument`` you will ensure that you
have implemented all the required methods used by PLACE during an experiment.
Start your instrument classes like this:

::

    from place.plugins.instrument import Instrument
    class MyDevice(Instrument):
        # (definition goes here) #

Currently, these are three methods you must implement.

\_\_init\_\_ (self, config, plotter)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Okay, technically, there are usually four methods you must implement,
and this is the fourth one. This is the standard constructor for Python.
We are passed the configuration data for our instrument, which should be
a Python dictionary. PLACE will just take it from the web interface and
send it to your code - simple as that!

As a subclass, we should ensure that the initializer of the base class
is called. There are `a number of ways to do
this <https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods>`__
in Python, but using the explicit call to the initializer works fine, I
think. Just call it like this:

::

    Instrument.__init__(self, config, plotter)

The Instrument initializer puts JSON data for your hardware into into
``self._config`` and sets ``self.priority`` to 100 (alhtough you usually
override this). This is done in the Instrument initializer because we need
to ensure that these two things are there for PLACE. All the other class
(self) variables can be determined as you see fit.

The ``plotter`` is also stored for you by the initializer, and accessible to the
instrument as ``self.plotter``. You can call this to register a plot which is
sent to the web interface. The plotter is an instance of the Plotter object in
``place/place/plots.py``, and has a variety of functions to help you easily
create plots of your data.

This method is not required, and if you find that you are just calling
the ``Instrument.__init__(self, config)`` listed above, and that's it,
then you might as well just omit the method. But typically, you will
find yourself putting something in here.

config(self, metadata, total\_updates)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method is called by PLACE at the beginning of the experiment. This
is when you should get everything up and running for the instrument.

As a convenience, the module is provided with the total number of times
the update method (the next method in this section) will be called for
your module.

Additionally, you will receive a ``metadata`` dictionary. This dictionary
holds values measured by devices at the start of an experiment. During
the ``config`` phase, you should add any values you would like to set
for the entire experiment. A common usage might be to record the serial
number and calibration data of the instrument you are using. **Please
avoid common names, since the dictionary is shared. Otherwise, you might
clobber data and invalidate an experiment.** The data recorded into the
metadata dictionary will be saved into the configuration data for the
experiment, stored as ``config.json`` in the experiment directory.

Note that, as a policy, instruments can only access the metadata before
the experiment begins. This is to reenforce the idea that metadata is
global for the experiment and known beforehand (a.k.a. not a
measurement). Anything that is measured should be recorded into the
NumPy array during the update phase.

update(self, update\_number, progress)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method is called by PLACE during the experiment. For example, one
experiment might take measurements from 100 different places on an
object. This means PLACE will call update on your method 100 times. Each
time it is called, you will need to do whatever it is your instrument
needs to do during that time. If your instrument is moving the object,
this is when you do that. If you are taking a measurement, then your
instrument needs to do that. PLACE isn't interested in what your
instrument actually does, it's just telling you that it's your turn.

You will receive a ``progress`` parameter, which is where the plotter records
plots, which are then returned to the user interface. This could be used by an
advanced user to send arbitrary data back to their web interface, but that use
case has not been developed or explored at this time.

You will also have access to the current update number, so your module
can plan accordingly.

cleanup(self, abort=False)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method is called by PLACE at the end of the experiment. It may also
be called if there is a problem with the experiment. Unfortunately,
there is no guarantee that this method will be called, so do as much as
possible to keep resources as free as possible. If this does get called,
though, your device should assume the experiment has ended and the code
should free all used resources.

If the ``abort`` parameter is set, this indicates that the experiment is
being abandoned, perhaps due to a safety concern, such as a problem with
one of the instruments. In this case, halting all real world activity
should be prioritized, and tasks regarding plotting, software resources
or data integrity can be skipped.

Serial port query
--------------------------

A new feature was added to PLACE in version 0.10.0 that allows us to
automatically identify whcih serial ports each instrument is connected to.
This is very useful, as you will know if you have ever tried to connect
more than one piece of equipment to a lab computer via a serial or USB port.
The serial_search.py script in the place directory performs this task for
us by examining the .place.cfg file for all the instruments that might be
connected via serial port. It then queries all instruments with the available
serial ports to try to identify which instrument is connected to which port before
updatin the .place.cfg file for us. This feature is best run by clicking the
"Serial Port Search" button in the "PLACE Configuration" tab of the web
interface). In order for this feature to talk to your instrument, you will
need to define a fifth function in your python plugin class called 
``serial_port_query``. 

serial_port_query(self, serial_port, field_name)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The idea of this function is that it takes a potential
``serial_port`` as an argument and tries to communicate with your instrument
on that port. If it gets a positive response that identifies your instrument,
then the function returns ``True`` to signify that the given port is the correct
one. If it does not get a positive response or an error occurs, then it will
return ``False``. The function must accept two parameters (aside from the necessary 
``self`` parameter): ``serial_port`` and ``field_name``. 



Writing a sample plugin
==================================

Deciding what the plugin will do
-----------------------------------------

The first step in developing your plugin is to decide what needs to be
automated. For this example, let automate a function generator in a
simple way. Let's say our function generator outputs a sine wave at a
specific frequency and we want to automate this so that each update is
performed at a different frequency.

We will start by figuring out what the code we would use if we were not
using PLACE. As a general rule, if you can't figure out how you would
code the solution outside of PLACE, then you probably aren't ready to
write a PLACE module. Let's say we communicate over a typical Linux
seral port and the instrument responds to ASCII commands specified in
the programmer's manual for the device. Our code will start at 100 Hz
and step by 5 Hz up to 200 Hz.

Our non-PLACE Python script to perform this would probably be something
like this:

::

    import serial

    with serial.Serial('/dev/ttyS0') as conn:
        for freq in range(100, 205, 5):
            conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

First round of adjustments
-------------------------------

So, we have the above script that performs an example of the task we want. The
first modification to make is to extract the values that may change, and assign
them to values. Later, we will put these values into our webapp so they can be
changed by the user. Looking at the above code, I would say that the variables
are: serial port path, first frequency, last frequency, and step. So let's move
those out of the code.

::

    import serial

    serial_port = '/dev/ttyS0'
    first_freq = 100
    last_freq = 200
    step_freq = 5

    end_freq = last_freq + step_freq

    with serial.Serial(serial_port) as conn:
        for freq in range(first_freq, end_freq, step_freq):
            conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

That looks better. Now all the values we may need to change are at the
top and will be easy for us to work with in the next steps.

Turn the code into a PLACE instrument class
-------------------------------------------------

PLACE will reject our module if it isn't a subclass of the Instrument
class built into PLACE. You can look at another module as a template,
but this is basically what you need.

::

    import serial

    from place.plugins.instrument import Instrument

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            serial_port = '/dev/ttyS0'
            first_freq = 100
            last_freq = 200
            step_freq = 5

            end_freq = last_freq + step_freq

            with serial.Serial(serial_port) as conn:
                for freq in range(first_freq, end_freq, step_freq):
                    conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

        def update(self, update_number, progress):
            pass

        def cleanup(self, abort=False):
            pass

This code is actually a fully functional PLACE module (minus a web
interface). This would work. Now, it wouldn't probably work as intended,
because everything happens during the *config* phase at the start of the
experiment. But, if it wasn't interacting with any other instruments,
this would do basically the same thing as our original script. Also,
notice that we had to name our class, and I chose to include the
fictional model number XY123 in the name. This prevents our code from
conflicting with other PLACE modules because it is much less likely to
have the same name as any other module.

Start leveraging the PLACE tools and information
----------------------------------------------------

So now that we have a PLACE module on our hands, we need to start
thinking about how to generalize our code to best work with PLACE. One
of the cornerstones of the PLACE software is that it allows users to
choose an arbitrary number of updates. This value is passed to us during
the *config* phase, and we should respond to it appropriately. In our
case, it means that we either need to fix the ``last_freq`` or the
``step_freq`` value and calculate the other based on the value of
``total_updates``. In this example, we will fix the ``step_freq``. We
get the following code:

::

    import serial

    from place.plugins.instrument import Instrument

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            serial_port = '/dev/ttyS0'
            first_freq = 100
            step_freq = 5
            last_freq = first_freq + (step_freq * total_updates)

            end_freq = last_freq + step_freq

            with serial.Serial(serial_port) as conn:
                for freq in range(first_freq, end_freq, step_freq):
                    conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

        def update(self, update_number, progress):
            pass

        def cleanup(self, abort=False):
            pass

While we're at it, we should talk about the other value we get during
the *config* phase, the ``metadata``. The ``metadata`` is a dictionary
which is passed around to all the modules during the config phase and it
is used to record data related to the entire experiment. A common use is
to put information into this dictionary that does not change during the
experiment, but may be needed in the future. One example might be
recording the ambient air temperature once at the start of the
experiment. In our case, we are going to put the ID string returned from
the function generator.

::

    import serial

    from place.plugins.instrument import Instrument

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            serial_port = '/dev/ttyS0'
            first_freq = 100
            step_freq = 5
            last_freq = first_freq + (step_freq * total_updates)

            end_freq = last_freq + step_freq

            with serial.Serial(serial_port) as conn:
                conn.write(bytes('*IDN?', 'ascii'))
                id_string = conn.readline()
            metadata['XY123-id-string'] = id_string.decode('ascii').strip()

            with serial.Serial(serial_port) as conn:
                for freq in range(first_freq, end_freq, step_freq):
                    conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

        def update(self, update_number, progress):
            pass

        def cleanup(self, abort=False):
            pass

The ID string is saved into a key in the dictionary that we select,
although it's important that we choose a unique key. Putting values into
the metadata is relatively arbitrary. Think of it as a notepad or
journal that will be saved into the experiment data.

Reading PlaceConfig values
---------------------------------

In our code, we have a value name ``serial_port`` that contains the
string path to find the port that connects to our instrument. This is a
bit of a special value because it is not likely to change very often,
but it is not likely to be the same for every computer. It is for this
reason that PLACE has a configuration API called PlaceConfig. Think of
it as a storage location for setting that shouldn't be in the webapp,
because they will almost always have the same value.

PLACE manages this file for you. It is always located in your Linux home
directory and is always named ``.place.cfg``. The PlaceConfig API is
based on the `configparser
library <https://docs.python.org/3/library/configparser.html>`__, which
is very easy to use.

Watch how we modify our code to store the serial port location in the
PLACE config file.

::

    import serial

    from place.plugins.instrument import Instrument
    from place.config import PlaceConfig

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            name = self.__class__.__name__
            serial_port = PlaceConfig().get_config_value(name, 'serial_port')
            first_freq = 100
            step_freq = 5
            last_freq = first_freq + (step_freq * total_updates)

            end_freq = last_freq + step_freq

            with serial.Serial(serial_port) as conn:
                conn.write(bytes('*IDN?', 'ascii'))
                id_string = conn.readline()
            metadata['XY123-id-string'] = id_string.decode('ascii').strip()

            with serial.Serial(serial_port) as conn:
                for freq in range(first_freq, end_freq, step_freq):
                    conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

        def update(self, update_number, progress):
            pass

        def cleanup(self, abort=False):
            pass

Pretty easy, right? You can read about PlaceConfig
`here <http://palab.github.io/place/config.html>`__. Basically, this one
command handles everything for you. If you ever need to change the
value, just edit ``~/.place.cfg`` and change the approprate value. PLACE
will automatically grab it the next time it runs.

Reading webapp/user data
-------------------------------

After reading what we can from PlaceConfig, we need to get anything else
we need from the user. The web interface module (which we'll talk about
later) should facilitate getting these options from the user to our
Python code. Here we will see how that works and, again, it's really
easy. Almost everything happens behind the scenes.

When PLACE initializes your module, all the settings provided by the webapp will
be put into your class. A special dictionary of values called ``_config`` is
included and will contain all the values you need. So, just get the values you
want from there... and at this stage, you can just name them anything you want.

::

    import serial

    from place.plugins.instrument import Instrument
    from place.config import PlaceConfig

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            name = self.__class__.__name__
            serial_port = PlaceConfig().get_config_value(name, 'serial_port')
            first_freq = self._config['first_freq']
            step_freq = self._config['step_freq']
            last_freq = first_freq + (step_freq * total_updates)

            end_freq = last_freq + step_freq

            with serial.Serial(serial_port) as conn:
                conn.write(bytes('*IDN?', 'ascii'))
                id_string = conn.readline()
            metadata['XY123-id-string'] = id_string.decode('ascii').strip()

            with serial.Serial(serial_port) as conn:
                for freq in range(first_freq, end_freq, step_freq):
                    conn.write(bytes('FREQ {}'.format(freq), 'ascii'))

        def update(self, update_number):
            pass

        def cleanup(self, abort=False):
            pass

Unlike metadata, ``self._config`` is available anywhere in your module,
so it can be used in the *update* and *cleanup* phases, too.

Move things into the correct methods
----------------------------------------

Up until now, we've put everything into the *config* method, meaning it
would all run at the beginning of the experiment. But, obviously, in
reality, we want the frequency to change during the *update* phase, so
that it happens at the correct time in relation to any other instruments
in the experiment. In this step, we will move the code that sets the
current frequency into the *update* method. We can also use the
``update_number`` parameter to calculate the correct frequency. All
these changes eliminate the need for our ``for`` loop, as PLACE
automatically calls *update* once for each update requested by the user.
This is pretty big change to our existing code, so see if you can follow
what happens here.

::

    import serial

    from place.plugins.instrument import Instrument
    from place.config import PlaceConfig

    class XY123FunctionGenerator(Instrument):

        def config(self, metadata, total_updates):

            name = self.__class__.__name__
            self.serial_port = PlaceConfig().get_config_value(name, 'serial_port')

            with serial.Serial(self.serial_port) as conn:
                conn.write(bytes('*IDN?', 'ascii'))
                id_string = conn.readline()
            metadata['XY123-id-string'] = id_string.decode('ascii').strip()

        def update(self, update_number):

            curr_freq = self._config['first_freq'] + (update_number * self._config['step_freq'])

            with serial.Serial(self.serial_port) as conn:
                conn.write(bytes('FREQ {}'.format(curr_freq), 'ascii'))

        def cleanup(self, abort=False):
            pass

The first thing that changed was that I added ``self`` onto the front of
``serial_port``, making it a class variable and allowing me to access it
from another method. Next I moved the frequency setting code into the
*update* method and used the value of ``update_number`` to calculate the
frequency for the *current update only*. This eliminated the need for
many of the variables I had been using to control the ``for`` loop.

Wraping up
------------------

That's basically it! We should be basically done. I hope you were able
to follow all of that. I promise that after a couple modules it becomes
second nature.

The last thing we want to do is make the ``__init__.py`` file for our
module. So we create a new file with that name. In this file, all we
need to do is import the class we created, allowing PLACE to see it. In
our case, the file needs one line, like this:

::

    from .xy123_function_gen import XY123FunctionGenerator

This assumes you named your module file ``xy123_function_gen.py``.

Alright! That's it for now.
