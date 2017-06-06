"""Main scan file for PLACE

This is the entry point for all PLACE scans. This also contains the code for
the PLACE server.
"""
import sys
import os
from operator import attrgetter
import json
from importlib import import_module
from asyncio import get_event_loop
import signal
import numpy as np
from numpy.lib import recfunctions as rfn
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from .plugins.instrument import Instrument

def osldv_scan(config, socket=None):
    """Run the OSLDV scan.

    :param config: a decoded JSON dictionary
    :type config: dict

    :param socket: a socket connected to the webapp for mpld3 data
    :type socket: websocket
    """
    # create the experiment directory
    config['directory'] = os.path.normpath(config['directory'])
    if not os.path.exists(config['directory']):
        os.makedirs(config['directory'])
    else:
        for i in range(1, 1000):
            if not os.path.exists(config['directory'] + '-' + str(i)):
                config['directory'] += '-' + str(i)
                break
        print('Experiment path exists - saving to ' + config['directory'])
        os.makedirs(config['directory'])
    with open(config['directory'] + '/config.json', 'x') as config_file:
        json.dump(config, config_file, indent=2)

    instruments = []
    _init_phase(instruments, config)

    metadata = {'comments': config['comments']}
    _config_phase(instruments, metadata, config['updates'], config['directory'])
    _update_phase(instruments, config['updates'], socket)
    _cleanup_phase(instruments, config['updates'], config['directory'], abort=False)

def basic_scan(config, socket=None):
    """Run a basic scan.

    :param config: a decoded JSON dictionary
    :type config: dict

    :param socket: a socket connected to the webapp for mpld3 data
    :type socket: websocket
    """
    # create the experiment directory
    config['directory'] = os.path.normpath(config['directory'])
    if not os.path.exists(config['directory']):
        os.makedirs(config['directory'])
    else:
        for i in range(1, 1000):
            if not os.path.exists(config['directory'] + '-' + str(i)):
                config['directory'] += '-' + str(i)
                break
        print('Experiment path exists - saving to ' + config['directory'])
        os.makedirs(config['directory'])
    with open(config['directory'] + '/config.json', 'x') as config_file:
        json.dump(config, config_file, indent=2)

    instruments = []
    _init_phase(instruments, config)

    metadata = {'comments': config['comments']}
    _config_phase(instruments, metadata, config['updates'], config['directory'])
    _update_phase(instruments, config['updates'], socket)
    _cleanup_phase(instruments, config['updates'], config['directory'], abort=False)

def _init_phase(instruments, config):
    """Initialize the instruments.

    During this phase, all instruments receive their configuration data and
    should store it. The list of instruments being used by the scan is created
    and sorted by their priority level. No physical configuration should occur
    during this phase.
    """
    for instrument_data in config['instruments']:
        module_name = instrument_data['module_name']
        class_string = instrument_data['class_name']
        priority = instrument_data['priority']
        config = instrument_data['config']

        instrument = _programmatic_import(module_name, class_string, config)
        instrument.priority = priority
        instruments.append(instrument)

    # sort instruments based on priority
    instruments.sort(key=attrgetter('priority'))

def _config_phase(instruments, metadata, total_updates, directory):
    """Configure the instruments.

    During the configuration phase, all instruments are provided with basic
    scan data.

    :param instruments: the instrument list for the scan
    :type instruments: list(Instrument)

    :param metadata: global metadata for the scan
    :type metadata: dict

    :param total_updates: total number of updates for this scan
    :type total_updates: int

    :param directory: the directory into which PLACE should write data
    :type directory: str
    """
    for instrument in instruments:
        print("...configuring {}...".format(instrument.__class__.__name__))
        instrument.config(metadata, total_updates)
    with open(directory + '/meta.json', 'x') as meta_file:
        json.dump(metadata, meta_file, indent=2)

def _update_phase(instruments, total_updates, socket):
    """Perform all the updates on the instruments.

    The update phase occurs N times, based on the user configuration for the
    scan. This function loops over the instruments (based on their priority)
    and calls their update method.

    :param instruments: the instrument list for the scan
    :type instruments: list(Instrument)

    :param total_updates: total number of updates for this scan
    :type total_updates: int

    :param socket: socket for sending data back to web interface
    :type socket: websocket
    """
    for update_number in range(total_updates):
        for instrument in instruments:
            print("...{}: updating {}...".format(update_number,
                                                 instrument.__class__.__name__))
            instrument.update(update_number, socket)

def _cleanup_phase(instruments, total_updates, directory, abort=False):
    """Cleanup the instruments.

    During this phase, each instrument has its cleanup method called. If the
    abort flag has not been set in the cleanup call, this will be passed to the
    instrument.

    During non-abort cleanup, NumPy record arrays will be collected from the
    instruments. These arrays should be N x M, where N is the number of updates
    in the scan. All the arrays will be appended together and written to disk.

    :param instruments: the instrument list for the scan
    :type instruments: list(Instrument)

    :param total_updates: total number of updates for this scan
    :type total_updates: int

    :param directory: the directory into which PLACE should write data
    :type directory: str

    :param abort: signals that a scan is being aborted
    :type abort: bool
    """
    if abort:
        for instrument in instruments:
            print("...aborting {}...".format(instrument.__class__.__name__))
            instrument.cleanup(abort=True)
    else:
        data = np.array(np.arange(total_updates), dtype=[('update', int)])
        for instrument in instruments:
            print("...cleaning up {}...".format(instrument.__class__.__name__))
            new_fields = instrument.cleanup(abort=False)
            if new_fields is not None:
                data = rfn.rec_join( #pylint: disable=redefined-variable-type
                    'update',
                    data, new_fields,
                    r2postfix='-'+instrument.__class__.__name__
                    )
        with open(directory + '/data.npy', 'xb') as data_file:
            np.save(data_file, data)

def scan_server(port=9130):
    """Starts a websocket server to listen for scan requests.

    This function is used to initiate a special scan process. Rather
    than specify the parameters via the command-line, this mode waits
    for scan commands to arrive via a websocket.

    Once this server is started, it will need to be killed via ctrl-c or
    similar.

    """
    def ask_exit():
        """Signal handler to catch ctrl-c (SIGINT) or SIGTERM"""
        loop.stop()

    async def scan_socket(websocket, _):
        """Creates an asyncronous websocket to listen for scans."""
        print("Waiting for scan...")
        sys.stdout.flush()
        # get a scan command from the webapp
        try:
            json_string = await websocket.recv()
        except ConnectionClosed as err:
            print("...connection closed: " + str(err))
        else:
            print("...scanning...")
            web_main(json_string, websocket)
            print("...scan complete.")

    print("Starting websockets server on port {}".format(port))
    loop = get_event_loop()
    # set up signal handlers
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame), ask_exit)
    coroutine = serve(scan_socket, 'localhost', port)
    # run websocket server
    server = loop.run_until_complete(coroutine)
    loop.run_forever()
    # cleanup
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

def main():
    """Command-line entry point for a scan."""
    # JSON data can be sent in through stdin
    if len(sys.argv[1:]) == 0:
        print('PLACE started: waiting for input...')
        _scan_main(json.loads(sys.stdin.read()))
    # or a filename can be specified using -f or --file
    elif len(sys.argv[1:]) == 2 and (sys.argv[1] == '-f' or sys.argv[1] == '--file'):
        with open(sys.argv[2]) as json_file:
            _scan_main(json.loads(json_file.read()))
    # or the JSON can just be the only argument
    elif len(sys.argv[1:]) == 1:
        _scan_main(json.loads(sys.argv[1]))
    # or the user did something weird
    else:
        print("Usage: place_scan '[JSON_STRING]'")
        print("       place_scan -f [JSON_FILE]")
        print("       place_scan --file [JSON_FILE]")
        print("       place_scan < [JSON_FILE]")
        sys.exit(-1)

def web_main(args, websocket=None):
    """Web entry point for a scan."""
    _scan_main(json.loads(args), websocket)

def _scan_main(config, websocket=None):
    if config['scan_type'] == 'basic_scan':
        basic_scan(config, websocket)
    elif config['scan_type'] == 'osldv_scan':
        osldv_scan(config, websocket)
    else:
        raise ValueError("invalid scan type: " + config['scan_type'])

def _programmatic_import(module_name, class_name, config):
    """Import an instrument based on string input.

    This function takes a string for a module and a string for a class and
    imports that class from the given module programmatically. It then creates
    and instance of that class and ensures it is a subclass of Instrument.

    :param module_name: the name of the module to import from
    :type module_name: str

    :param class_name: the string of the class to import
    :type class_name: str

    :param config: the JSON configuration data for the instrument
    :type config: dict

    :returns: an instance of the instrument matching the class and module
    :rtype: Instrument

    :raises TypeError: if requested instrument has not been subclassed correctly
    """
    module = import_module('place.plugins.' + module_name)
    class_ = getattr(module, class_name)
    if not issubclass(class_, Instrument):
        raise TypeError(class_name + " is not a subclass of Instrument")
    return class_(config)
