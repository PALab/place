
# PLACE 

PLACE is an open-source Python package for laboratory automation, control, and experimentation.  

It provides driver modules for automating laboratory instruments, example implementation scripts, and modules for visualizing and processing waveform data (available with PALplots: https://github.com/PALab/PALplots).

A goal of PLACE is to develop a repository of instrument drivers for laboratory automation.  In addition, rapid development of compatible processing software will streamline laboratory activity from acquisition through data analysis.

## Installation

### Install PLACE via conda

```
conda install -c defaults -c conda-forge -c freemapa place
pip install obspyh5 websockets
```

### Build PLACE from source

You can build PLACE on your own *(perhaps if you need to support another version of Python)*. Simply checkout the repository and run the following conda command:

```
conda build place -c defaults -c conda-forge
```

Install the local build:

```
conda install place --force --use-local --offline
```

## Running PLACE

### Control PLACE via the command-line interface

```
place_scan [options]
```

Run `place_scan --help` for options.

### Control PLACE via webapp (requires Python >= 3.5)

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

