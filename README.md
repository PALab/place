
# PLACE 

PLACE is an open-source (P)ython package for (L)aboratory (A)utomation,
(C)ontrol, and (E)xperimentation.  

PLACE provides a modular framework for automating laboratory instruments and
managing the data acquisition process during experiments.  PLACE already
contains modules for many popular instruments and the continuing goal of PLACE
is to develop additional modules for laboratory automation.

## Citing PLACE
If you use PLACE for work resulting in a publication, please acknowledge the
package by citing the following paper:

Johnson, Jami L., Henrik tom Wörden, and Kasper van Wijk. "[PLACE An
Open-Source Python Package for Laboratory Automation, Control, and
Experimentation](http://jla.sagepub.com/content/20/1/10)." Journal of
laboratory automation (2014): 2211068214553022.

# Installation

## Quick install

To ease installation, PLACE is hosted on [Anaconda Cloud](https://anaconda.org),
under the *freemapa* channel.

```
conda install -c freemapa place
```

## Installation Details

This section will walk you through a more detailed installation of PLACE.
PLACE can be installed for Linux 32/64-bit running Python 3.5 or later.
Support for Windows and Mac is limited and still experimental. This
installation has been performed multiple times on many Ubuntu and CentOS
distributions.

### Install Anaconda

If you don't have conda, you will need to install it. This guide used the
Python 3.6 version of Anaconda 5.2.0 for Linux 64-bit systems. In any event,
Anaconda can be found [here](https://www.continuum.io/downloads). Just follow
the instructions to get it installed on your system.

*Note:* Anaconda will install its own copy of Python. It will leave any
existing versions on your system. It also contains its own location for storing
Python libraries. If you encounter conflicts, it is likely due to preexisting
installations (via yum, apt, pip, etc).

### Install PLACE

At this point, you should be able to perform the conda install command.

```
conda install -c freemapa place
```

If conda cannot find all the packages needed by PLACE, you may need to
include the *conda-forge* channel.

```
conda install -c conda-forge -c freemapa place
```

### PLACE configuration

All the configuration options for PLACE are put into a file in your home
directory named `~/.place.cfg`. Typically, this file includes information
needed to connect to the various hardware components running in PLACE. It is
not mandatory to set this up before running PLACE, but PLACE will display an
error message if it is unable to find a needed value.

To find out which values are needed for the instruments you are using, read the
documentation for the PLACE plugin for that instrument. Alternatively, ask
someone who has already used the instrument to provide you with the needed
`.place.cfg` values. Remember that each user has their own `~/.place.cfg` file,
so if you are setting up a new user on an existing system, it may be useful to
provide them with a copy of the `~/.place.cfg` file from another user.

It should also be noted that Linux users generally do not have write access
to serial ports. This is needed by many hardware devices. To ensure serial
communication is available, an administrator should add PLACE users to the
*dialout* group.

```
sudo usermod -a -G dialout <username>
```

## Build PLACE from source (Advanced)

You can build PLACE on your own *(perhaps if you need to support another
version of Python)*. Simply clone the Git repository:

```
git clone https://github.com/PALab/place.git
```

Now we need to install the source code.

**Note** - Before installing from source, it would be best to remove any
existing versions of PLACE you have installed.

So, at this point, you have two options. The first option works for most cases.

### Option 1: Install a development build

Installing a development build does not actually install anything. It just
points the executable files to the directory containing the source code. This
means that any changes you make to the source code will be reflected almost
immediately in PLACE.

To install a development build, from the ``place`` directory, run:

```
python setup.py develop
```

When you are finished running the development build, you run:

```
python setup.py develop --uninstall
```

And then, to check the uninstallation you may need to ensure the PLACE
executables have been removed. Run ``which place_server`` and, if it finds
something, go to that directory and delete all the ``place_*`` executable files.

Use this option with care. It often seems like less work up front, but can cause
problems down the road. It is common to forget you've installed a development
build and then accidentally install a regular build as well, leading to great
confusion.

### Option 2: Install a proper build

This option build a proper package of all the source code (like you would get
from conda) and manually installs it. This method takes much longer, but is
better if you are going to be using the build for more than just testing.

Run the following build command:

```
conda build place
```

Install the local build:

```
conda install place --use-local
```

*Note:* Installing a local copy will not always install the dependencies, so
manually installing the required packages listed in the `meta.yaml` file may be
required.

The advantage to this method is that if you ever need to uninstall PLACE, you
have conda do it for you.

```
conda remove place
```

## Install an Elm build environment

The frontend of PLACE is built using Elm. Elm is built on top of the Node.js
JavaScript runtime. Therefore, in order to develop the graphical frontend
modules for PLACE, you will need to install both Node.js and Elm.

### Node.js

Installing Node.js should be relatively easy on Windows or MacOS, as there are
[installers for both](https://nodejs.org/en/download/). If you are installing
on Linux, you will likely need to get Node.js from an
[app repository](https://nodejs.org/en/download/package-manager/) or build
it from source.

### Elm

After getting Node.js installed, you should be able to install Elm by simply
running:

```
npm install -g elm@0.18
```

Note that PLACE has not been updated for the recently released Elm version 0.19.
Until this update, you must specify installing version 0.18.

If you are installing ``elm``, I would suggest installing ``elm-format`` as well.
It is a useful tool, as it will automatically format all Elm code to use the same
style.

```
npm install -g elm-format
```

### CentOS 7 tips

Having installed Elm on CentOS a couple times, I can say that it can be slightly
more difficult. Personally, I have had success with the following commands.
(Current as of March 2018)

```
curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
sudo yum -y install nodejs
sudo npm i -g elm@0.18 --unsafe-perm=true --allow-root
sudo npm i -g elm-format --unsafe-perm=true --allow-root
```

## PLACE config file

PLACE will create a config file in the following location: `~/.place.cfg`

You can manually create this file if it does not exist. System dependent
variables are placed in this file. Typically, this will include things like: IP
addresses to network assets, serial connections to instruments, or other global
settings. PLACE modules are free to use this file as needed, so an exhaustive
list cannot be provided. However, PLACE should throw errors if values are not
populated correctly and should direct you when you need to edit this file.  The
config file follows a very basic syntax for declaring name/value pairs.

```
[Section]
name = value
another = more
```

If PLACE informs you that a value is missing from this file, it should populate
the file with a default value. You can then edit the file and update the
necessary value. Then rerun PLACE. If you are writing modules, PLACE provides a
simple API that handles accessing values from this file.

# Running PLACE

PLACE should be controlled using the web interface. The web interface is hosted
directly by the PLACE server. To start the PLACE server, simply run the service
from the command line:

```
place_server
```

The server will print the IP address you need to access the web interface.
Simple type the address into your browser to begin using PLACE.

**Note** - Currently the PLACE web interface is only known to work on [Google
Chrome](https://www.google.com/chrome/). Future versions are intended to work
on all modern web browsers.

**Update (November 2018)** - Other browsers seem to work fine now, but let us
know if you notice any issues.

## Control PLACE via the command-line interface

Running PLACE from the command-line is no longer supported, although it should
still be possible. Please let us know if this feature is of interest to you.

## PLACE execution

After receiving JSON data, PLACE will attempt to perform an experiment based on
this data. The server provides on-demand updates of the experimental progress
and the web interface is designed to check periodically. Errors will usually
print on the server, so check the output there if the web interface doesn't seem
to be getting any updates.

The server will wait for additional experiments after the current experiment is
completed.

# Other PLACE topics

## Writing PLACE modules

[Writing the Python backend](http://palab.github.io/place/backend_tutorial.html)

[Writing the Elm frontend](http://palab.github.io/place/frontend_tutorial.html)

# Authors

Jami L Johnson

Henrik tom Wörden

Kasper van Wijk

Paul Freeman
