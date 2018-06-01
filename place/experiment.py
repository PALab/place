"""Main file for PLACE

This is the entry point for all PLACE experiments. This also contains the code
for the PLACE server.
"""
__version__ = "0.7.0"

import threading
from .basic_experiment import BasicExperiment

LOCK = threading.Lock()
WORKER = None
WORK_THREAD = None
READY = 'Ready'
BUSY = 'Busy'
STARTED = 'Started'

def start(config):
    """Attempt to start a PLACE experiment"""
    global WORKER, WORK_THREAD # pylint: disable=global-statement
    if LOCK.acquire(blocking=False):
        WORKER = BasicExperiment(config)
        WORK_THREAD = threading.Thread(target=WORKER.run)
        WORK_THREAD.start()
        return STARTED
    return BUSY

def status():
    """Get the status of PLACE"""
    if not LOCK.acquire(blocking=False):
        WORK_THREAD.join(timeout=0.1)
        if WORK_THREAD.is_alive():
            return WORKER.get_progress_string()
    LOCK.release()
    return READY

def start_experiment(config):
    """Start a blocking experiment
    
    Used mostly for testing.
    """
    global WORKER, WORK_THREAD # pylint: disable=global-statement
    with LOCK.acquire():
        WORKER = BasicExperiment(config)
        WORK_THREAD = threading.Thread(target=WORKER.run)
        WORK_THREAD.start()
        while True:
            WORK_THREAD.join(timeout=0.5)
            if not WORK_THREAD.is_alive():
                break
            print(WORKER.get_progress_string())
