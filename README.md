
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

The current version of Python (as of March 2017) is 3.6 but PLACE currently requires Python 3.5. Not to worry, though, because we can create a Python 3.5 environment easily with conda.

```
conda create --name place_env -c defaults -c conda-forge -c freemapa place
```

This command does it all! It creates an environment that is compatible with the
current version of PLACE and installs all the dependencies. In this case, it
automatically sees that PLACE requires Python 3.5 and installs it into the
environment. The purpose of all the `-c` arguments is to prioritise from where
to get dependent library files. First, the *default* channel is checked, then
the *conda-forge* channel, and finally, the *freemapa* channel (where PLACE is
hosted).

Don't forget that Python 3.6 is still installed on your system. To use PLACE,
we must activate our PLACE environment. We do this with the following command.

```
source activate place_env
```

This command changes all the environment variables to point to Python 3.5
instead of 3.6. It also makes sure we have access to all those dependent
libraries we need. If we need to go back to Python 3.6 for some reason, we use
the following command.

```
source deactivate place_env
```

At this point, you should be all set to start using PLACE.

## Build PLACE from source (Advanced)

You can build PLACE on your own *(perhaps if you need to support another
version of Python)*. Simply checkout the repository and run the following conda
command:

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

# Running PLACE

## Control PLACE via the command-line interface

```
place_scan [options]
```

Run `place_scan --help` for options.

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
