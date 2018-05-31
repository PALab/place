"""Main file for PLACE

This is the entry point for all PLACE experiments. This also contains the code
for the PLACE server.
"""
__version__ = "0.7.0"

from .config import PlaceConfigError
from .basic_experiment import BasicExperiment

def start_experiment(config):
    """Perform a PLACE experiment"""
    print("...starting experiment...")
    try:
        BasicExperiment(config).run()
        print("...experiment complete...")
    except PlaceConfigError as err:
        print("!!!!! {}".format(err))
