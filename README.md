
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

## Installation

### Install PLACE via conda
To ease installation, PLACE is hosted on [Anaconda
Cloud](https://anaconda.org), under the *freemapa* channel. Additionally, we
require several packages provided on the *conda-forge* channel.

```
conda install -c defaults -c conda-forge -c freemapa place
```
Please note that PLACE currently will only work on Python 3.5. Support for
Python 3.6 will be provided once our dependent libraries have been updated.

### Build PLACE from source

You can build PLACE on your own *(perhaps if you need to support another
version of Python)*. Simply checkout the repository and run the following conda
command:

```
conda build place -c defaults -c conda-forge
```

Install the local build:

```
conda install place --use-local
```
Please note that installing a local copy will not always install the
dependencies, so installing the required packages listed in the meta.yaml file
manually may be required.

## Running PLACE

### Control PLACE via the command-line interface

```
place_scan [options]
```

Run `place_scan --help` for options.

### Control PLACE via webapp

```
place_server
```

When the server launches, it will display a randomly generated 4-digit
key. You must enter this correctly into the webapp in order for the scan
to be accepted by the server.

Access the webapp by opening place/web/place.html in any web browser.



## Authors

Jami L Johnson

Henrik tom Wörden

Kasper van Wijk

