"""Main file for PLACE

This is the entry point for all PLACE experiments. This also contains the code
for the PLACE server.
"""
import sys
import json
from asyncio import get_event_loop
import signal
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from .basic_experiment import BasicExperiment

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
            web_main(json_string)
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
    """Command-line entry point for an experiment."""
    # JSON data can be sent in through stdin
    if len(sys.argv[1:]) == 0:
        print('PLACE started: waiting for input...')
        _scan_main(json.loads(sys.stdin.read()))
    # or a filename can be specified using -f or --file
    elif len(sys.argv[1:]) == 2 and (sys.argv[1] == '-f' or sys.argv[1] == '--file'):
        with open(sys.argv[2]) as json_file:
            _scan_main(json.load(json_file))
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

def web_main(args):
    """Web entry point for a scan."""
    _scan_main(json.loads(args))

def _scan_main(config):
    BasicExperiment(config).run()
