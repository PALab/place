"""A worker thread for running PLACE experiments

Currently, there exists one thread for running PLACE experiments, and there
is no queue for submitting multiple jobs. You must ensure PLACE is not busy
before starting a new experiment. Basically, this means you should call the
status function until PLACE says it is ready. Then you can submit a new
experiment.
"""

import threading
from place.basic_experiment import BasicExperiment

LOCK = threading.Lock()
WORKER = None
WORK_THREAD = None
READY = 'Ready'
RUNNING = 'Running'
STARTED = 'Started'
QUEUED = 'Queued'


def start(config):
    """Attempt to start a PLACE experiment

    :returns: either a *started* or *busy* message
    :rtype: str
    """
    global WORKER, WORK_THREAD  # pylint: disable=global-statement
    if LOCK.acquire(blocking=False):
        WORKER = BasicExperiment(config)
        WORK_THREAD = threading.Thread(target=WORKER.run)
        WORK_THREAD.start()
        return STARTED
    return RUNNING


def status():
    """Get the status of PLACE

    :returns: either a progress string or the *ready* message
    :rtype: str
    """
    if not LOCK.acquire(blocking=False):
        WORK_THREAD.join(timeout=0.1)
        if WORK_THREAD.is_alive():
            return {'status': RUNNING, 'progress': WORKER.get_progress()}
    LOCK.release()
    return {'status': READY}


def start_experiment(config):
    """Start a blocking experiment

    Used mostly for running tests during the PLACE build.
    """
    global WORKER, WORK_THREAD  # pylint: disable=global-statement
    with LOCK.acquire():
        WORKER = BasicExperiment(config)
        WORK_THREAD = threading.Thread(target=WORKER.run)
        WORK_THREAD.start()
        while True:
            WORK_THREAD.join(timeout=0.5)
            if not WORK_THREAD.is_alive():
                break
            print(WORKER.get_progress())
