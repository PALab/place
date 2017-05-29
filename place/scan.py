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
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from .plugins.instrument import Instrument

def basic_scan(config, socket=None):
    """Run a basic scan.

    :param config: a decoded JSON dictionary
    :type config: dict

    :param socket: a socket connected to the webapp for mpld3 data
    :type socket: websocket

    :raises TypeError: if requested instrument has not been subclassed correctly
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
    _config_phase(instruments, config, metadata)
    _update_phase(instruments, config, metadata, socket)
    _cleanup_phase(instruments)

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

        # import module programmatically
        module = import_module('place.plugins.' + module_name)
        class_name = getattr(module, class_string)
        if not issubclass(class_name, Instrument):
            raise TypeError(class_string + " is not a subclass of Instrument")
        instrument = class_name(config)

        # set priority
        instrument.priority = priority

        # add to the list of instruments
        instruments.append(instrument)

    # sort instruments based on priority
    instruments.sort(key=attrgetter('priority'))

def _config_phase(instruments, config, metadata):
    """Configure the instruments.

    During the configuration phase, all instruments are provided with basic
    scan data.
    """
    for instrument in instruments:
        print("...configuring {}...".format(instrument.__class__.__name__))
        updates = config['updates']
        directory = config['directory'] + '/' + instrument.__class__.__name__
        os.makedirs(directory)
        instrument.config(metadata, updates, directory)

def _update_phase(instruments, config, metadata, socket):
    """Perform all the updates on the instruments.

    The update phase occurs N times, based on the user configuration for the
    scan. This function loops over the instruments (based on their priority)
    and calls their update method.
    """
    for update_number in range(1, config['updates']+1):
        metacopy = metadata.copy()
        for instrument in instruments:
            print("...{}: updating {}...".format(update_number,
                                                 instrument.__class__.__name__))
            instrument.update(metacopy, update_number, socket)

def _cleanup_phase(instruments):
    """Cleanup the instruments.

    During this phase, each instrument has its cleanup method called.
    """
    # 3 - cleanup
    for instrument in instruments:
        print("...cleaning up {}...".format(instrument.__class__.__name__))
        instrument.cleanup()

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
