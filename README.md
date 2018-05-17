
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

To ease installation, PLACE is hosted on [Anaconda
Cloud](https://anaconda.org), under the *freemapa* channel. Additionally, we
require several packages provided on the *conda-forge* channel.

```
conda install -c freemapa place
```

## Installation Details

This section will walk you through a more detailed installation of PLACE.
PLACE can be installed for Linux 32/64-bit running Python 3.5 or later.  This
installation has been specifically tested on a clean installation of Ubuntu
16.04.2 LTS. PLACE has also been used on CentOS 7 systems.

### Install Anaconda

If you don't have conda, you will need to install it. This guide used the
Python 3.6 version of Anaconda 4.3.1 for Linux 64-bit systems. In any event,
Anaconda can be found [here](https://www.continuum.io/downloads). Just follow
the instructions to get it installed on your system.

*Note:* Anaconda will install its own copy of Python. It will leave any
existing versions on your system. It also contains its own location for storing
Python libraries. If you encounter conflicts, it is likely due to preexisting
installations (via yum, apt, pip, etc).

At this point, you should be able to perform the quick install command listed
above.

## Build PLACE from source (Advanced)

You can build PLACE on your own *(perhaps if you need to support another
version of Python)*. Simply clone the Git repository:

```
git clone https://github.com/PALab/place.git
```

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

After getting Node.js installed, you should be able to install Elm by simple
running:

```
npm install -g elm
```

### CentOS 7 tips

Having installed Elm on CentOS a couple times, I can say that it can be slightly
more difficult. Personally, I have had success with the following commands.
(Current as of March 2018)

```
curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
sudo yum -y install nodejs
sudo npm i -g elm --unsafe-perm=true --allow-root
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

## Control PLACE via webapp (recommended)

PLACE can (and should) be controlled using the web interface. The latest
version of the web interface is hosted [on the PLACE
webpage](https://place.auckland.ac.nz). The webpage runs JavaScript to connect
to a locally running PLACE server. To start the PLACE server, simply run the
service from the command line:

```
place_server
```

If the server connects to the webpage, you will see a message stating that the
server is waiting for experimental data. You can then use the web interface to
start experiments.

**Note:** Currently the PLACE web interface is only known to work on [Google
Chrome](https://www.google.com/chrome/). Future versions are intended to work
on all modern web browsers.

## Control PLACE via the command-line interface

Running PLACE from the command-line interface is possible, too. However, as
even a simple experiment can require tens or even hundreds of options, this
interface is not recommended.

PLACE options must be formatted into a JSON file, with the options split into
groups, depending on the instrument they need to be sent to. The web interface
provides a JSON view to give you an idea for how to format the options. It is
suggested that the options by put into a file and passed to PLACE using the
`--file` command-line option.

```
place_experiment --file <JSON-file>
```

There are alternative ways of passing data to PLACE, including pipes or
directly from the keyboard, but they are not explained here.

## PLACE execution

After receiving JSON data, PLACE will attempt to perform an experiment based on
this data. Currently, all PLACE output is directed to the command-line, so the
web interface cannot relay the running status of PLACE. Please check the
`place_server` for any important output or errors.

When using the server, it will wait for additional experiments after the
current experiment is completed. When running experiments without the server,
PLACE will exit after each experiment.

# Other PLACE topics

## Writing PLACE modules

[Writing the Python backend](http://palab.github.io/place/backend_tutorial.html)

[Writing the Elm frontend](http://palab.github.io/place/frontend_tutorial.html)

# Authors

Jami L Johnson

Henrik tom Wörden

Kasper van Wijk

Paul Freeman
