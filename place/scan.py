"""New scan file for PLACE 0.3
"""
import sys
from operator import attrgetter
import json
from importlib import import_module
from asyncio import get_event_loop
import signal
from websockets.server import serve
from obspy.core.trace import Stats
from .plugins.instrument import Instrument

class Scan:
    """An object to describe a scan experiment"""
    def __init__(self):
        self.scan_config = None
        self.scan_type = None
        self.instruments = []
        self.header = None

    def config(self, config_string):
        """Configure the scan

        :param config_string: a JSON-formatted configuration
        :type config_string: str
        """
        self.header = Stats()
        self.scan_config = json.loads(config_string)
        self.scan_type = self.scan_config['scan_type']
        for instrument_data in self.scan_config['instruments']:
            module_name = instrument_data['module_name']
            class_string = instrument_data['class_name']
            priority = instrument_data['priority']
            config = instrument_data['config']

            module = import_module('place.plugins.' + module_name)
            class_name = getattr(module, class_string)
            if not issubclass(class_name, Instrument):
                raise TypeError(class_string + " is not a subclass of Instrument")
            instrument = class_name()
            instrument.config(self.header, json.dumps(config))
            instrument.priority = priority
            self.instruments.append(instrument)
        self.instruments.sort(key=attrgetter('priority'))

    def run(self):
        """Perform the scan"""
        if self.scan_type == "scan_point_test":
            for instrument in self.instruments:
                instrument.update(self.header)
            for instrument in self.instruments:
                instrument.cleanup()
        else:
            raise ValueError('invalid scan type')

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
        json_string = await websocket.recv()
        web_main(json_string)
        await websocket.send("Scan received")
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
    """Command-line entry point for a 0.3 scan."""
    scan = Scan()
    scan.config(sys.argv[1])
    scan.run()

def web_main(args):
    """Web entry point for a 0.3 scan."""
    scan = Scan()
    scan.config(args)
    scan.run()
