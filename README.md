
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

## Running PLACE

### Control PLACE via the command-line interface

```
place_scan [options]
```

Run `scan --help` for options.

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

