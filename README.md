
# PLACE 

PLACE is an open-source Python package for laboratory automation, control, and
experimentation.  

It provides driver modules for automating laboratory instruments, example
implementation scripts, and modules for visualizing and processing waveform
data (available with PALplots: https://github.com/PALab/PALplots).

The goal of PLACE is to develop a repository of instrument drivers for
laboratory automation.  In addition, rapid development of compatible processing
software will streamline laboratory activity from acquisition through data
analysis.

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
conda install -c defaults -c conda-forge -c freemapa place
```

## Installation Details

This section will walk you through a more detailed installation of PLACE. This
has been tested on a clean installation of Ubuntu 16.04.2 LTS.

### Install Anaconda

If you don't have conda, you will need to install it. This guide used the
Python 3.6 version of Anaconda 4.3.1 for Linux 64-bit systems. In any event,
Anaconda can be found [here](https://www.continuum.io/downloads). Just follow
the instructions to get it installed on your system.

*Note:* Anaconda will install its own copy of Python. It will leave any
existing versions on your system. It also contains its own location for storing
Python libraries. If you encounter conflicts, it is likely due to preexisting
installations (via yum, apt, pip, etc).

### Create a conda environment

The current version of Python (as of March 2017) is 3.6 but PLACE currently
requires Python 3.5. Not to worry, though, because we can change the version of
Python easily.

```
conda install python=3.5
```

At this point, you should be all set to start using PLACE.

## Build PLACE from source (Advanced)

You can build PLACE on your own *(perhaps if you need to support another
version of Python)*. Simply checkout the repository and run the following
commands:

```
git clone https://github.com/PALab/place.git
conda build place -c defaults -c conda-forge
```

Install the local build:

```
conda install place --use-local
```

*Note:* Installing a local copy will not always install the dependencies, so
installing the required packages listed in the `meta.yaml` file manually may be
required.

# Before using PLACE

A small amount of setup must be done to customize the driver modules to fit a
specific instrument and acquisition PC:

## PLACE config file

PLACE will create a config file in the following location: `~/.place.cfg`

You can manually create this file if it does not exist. System dependent
variables are placed in this file and PLACE will throw errors if they are not
populated correctly. The config file follows a very basic syntax for declaring
name/value pairs.

```
[Section]
name = value
another = more
```

The following sections will tell which values must be set to support certain
operations.

*Note:* It is possible that these names may have changed, or new values are
required. In other words, this README may not alway be up to date with the
latest code changes. But not to worry, PLACE should automatically insert
default values into the config file if no existing value is found, which can
then be edited to suit your lab setup.

### Tektronix oscilloscope

The Tektronix oscilloscope requires the IP address to be set.

```
[Tektronix]
ip_address = 192.168.0.0
```

### Polytec vibrometer

The vibrometer requires the RS-232 connection to be set (e.g. COM1, /dev/ttyS0,
etc.).

```
[Polytec]
port = /dev/ttyS0
```

### XPS controller

The IP address for the picomotor controller and other controller must be set.

```
[XPS]
picomotor controller IP address = 130.216.58.155
other controller IP address = 130.216.58.154
```

# Running PLACE

## Control PLACE via the command-line interface

```
place_scan [JSON-options]
```

## Control PLACE via webapp

```
place_server
```

When the server launches, it will display a randomly generated 4-digit
key. You must enter this correctly into the webapp in order for the scan
to be accepted by the server.

Access the webapp by opening place/web/place.html in any web browser.

# Authors

Jami L Johnson

Henrik tom Wörden

Kasper van Wijk

Paul Freeman
