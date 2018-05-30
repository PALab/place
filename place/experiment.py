"""Main file for PLACE

This is the entry point for all PLACE experiments. This also contains the code
for the PLACE server.
"""
__version__ = "0.7.0"

import sys
import json
from .celery import app as celery_app
from .config import PlaceConfigError
from .basic_experiment import BasicExperiment

def start(config):
    """Start a PLACE experiment"""
    start_experiment.delay(config)

@celery_app.task
def start_experiment(config):
    """Perform a PLACE experiment"""
    print("...starting experiment...")
    try:
        BasicExperiment(config).run()
        print("...experiment complete...")
    except PlaceConfigError as err:
        print("!!!!! {}".format(err))

def main():
    """Command-line entry point for an experiment."""
    if not sys.argv[1:]:
        print('PLACE started: please use your keyboard')
        print('(or copy/paste) to input JSON experiment data...')
        start_experiment.delay(json.loads(sys.stdin.read()))
    elif len(sys.argv[1:]) == 2 and (sys.argv[1] == '-f' or sys.argv[1] == '--file'):
        with open(sys.argv[2]) as json_file:
            start_experiment.delay(json.load(json_file))
    elif len(sys.argv[1:]) == 1:
        start_experiment.delay(json.loads(sys.argv[1]))
    else:
        print("Usage: place_experiment '[JSON_STRING]'")
        print("       place_experiment -f [JSON_FILE]")
        print("       place_experiment --file [JSON_FILE]")
        print("       place_experiment < [JSON_FILE]")
        sys.exit(-1)
