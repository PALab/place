"""Main scan file for PLACE

This is the entry point for all PLACE scans. This also contains the code for
the PLACE server.
"""
import sys
from operator import attrgetter
import json
from importlib import import_module
from asyncio import get_event_loop
import signal
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from obspy import Stream
from obspy.core.trace import Stats
# obspyh5 is a non-standard module and sets itself up during import. Therefore,
# even though it is never called in this file, it is still necessary to import
# it. Pylint does not like this and complains that it is never used. So, we
# must disable this check for this line only.
import obspyh5 # pylint: disable=unused-import
from .plugins.instrument import Instrument

class Scan:
    """An object to describe a scan experiment.

    This scan provides instrument configuration only does not save any data
    collected. It is mostly used as a base class for other scans, although it
    may be useful for testing. Usually you will use a subclass of this for your
    actual scan.
    """
    def __init__(self, config):
        """Configure the scan.

        :param config: a decoded JSON dictionary
        :type config: dict

        :raises TypeError: if requested instrument has not been subclassed correctly
        """
        # save JSON data
        self._config = config

        # import all instruments and set priorities
        self._instruments = []
        for instrument_data in self._config['instruments']:
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
            self._instruments.append(instrument)

        # sort instruments based on priority
        self._instruments.sort(key=attrgetter('priority'))

    def run(self):
        """This scan updates every instrument once."""
        for instrument in self._instruments:
            instrument.config()
        for instrument in self._instruments:
            instrument.update()
        for instrument in self._instruments:
            instrument.cleanup()

class BasicScan(Scan):
    """A basic scan.

    This scan provides a preset number of updates and runs automatically. Trace
    data is saved to an HDF5 file. Plots are supported if using the webapp.
    """
    def __init__(self, config, plot=None):
        """Configure the scan

        :param config: a decoded JSON dictionary
        :type config: dict

        :param plot: a socket connected to webapp for mpld3 data
        :type plot: websocket
        """
        # Initialize the config data and instrument list
        Scan.__init__(self, config)

        # Create header object
        self._header = Stats()
        self._header['comments'] = self._config['comments']

        # Save a socket to write the plot to the webapp iframe
        self._plot = plot

    def run(self):
        """Call update the number of times specified and then cleanup."""
        for instrument in self._instruments:
            print("...configuring {}...".format(instrument.__class__.__name__))
            instrument.config()
        for i in range(self._config['updates']):
            for instrument in self._instruments:
                print("...{}: updating {}...".format(i, instrument.__class__.__name__))
                instrument.update(
                    header=self._header,
                    socket=self._plot)
        stream = Stream()
        for instrument in self._instruments:
            print("...cleaning up {}...".format(instrument.__class__.__name__))
            stream += instrument.cleanup()
            obspyh5.set_index('PLACE.BasicScan/' + instrument.__class__.__name__ +
                              '/{starttime.datetime:%Y-%m-%dT%H:%M:%S.%f}_' +
                              '{endtime.datetime:%Y-%m-%dT%H:%M:%S.%f}')
            stream.write(self._config['filename'], 'H5', mode='a', override='raise')

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
    if config['scan_type'] == 'test_scan':
        Scan(config).run()
    if config['scan_type'] == 'basic_scan':
        BasicScan(config, websocket).run()
