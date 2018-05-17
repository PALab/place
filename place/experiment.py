"""Main file for PLACE

This is the entry point for all PLACE experiments. This also contains the code
for the PLACE server.
"""

__version__ = "0.6.4"

import sys
import time
import json
import asyncio
import signal
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
from .config import PlaceConfigError
from .basic_experiment import BasicExperiment

def experiment_server(port=9130):
    """Starts a websocket server to listen for experiment requests.

    This function is used to initiate an experiment server. Rather
    than specify the parameters via the command-line, this mode waits
    for PLACE experiment configuration to arrive via a websocket.

    Once this server is started, it will need to be killed via ctrl-c or
    similar.

    """
    def ask_exit():
        """Signal handler to catch ctrl-c (SIGINT) or SIGTERM"""
        for task in asyncio.Task.all_tasks():
            task.cancel()
        time.sleep(1)
        loop.stop()


    async def experiment_socket(websocket, _):
        """Creates an asyncronous websocket to listen for experiments."""
        try:
            print("...webapp detected - sending connection message...")
            await websocket.send('<VERS>' + __version__)
            print("...waiting for experiment configuration data...")
            sys.stdout.flush()
            json_string = await websocket.recv()
            print("...starting experiment...")
            try:
                web_main(json_string)
                print("...experiment complete...")
            except PlaceConfigError as err:
                print("!!!!! {}".format(err))
        except ConnectionClosed as err:
            print("...connection closed: " + str(err))
        except asyncio.CancelledError:
            print('...server close requested - notifying webapp...')
            await websocket.send('<CLOS>')


    print("PLACE " + __version__ + " | Author: Paul Freeman | 2018")
    print("Originally created by: Jami L Johnson, Henrik tom Wörden, and Kasper van Wijk")
    loop = asyncio.get_event_loop()
    try:
        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, signame), ask_exit)
    except NotImplementedError:
        pass
    coroutine = serve(experiment_socket, 'localhost', port)
    server = loop.run_until_complete(coroutine)
    print('Server started...')
    loop.run_forever()
    server.close()
    loop.run_until_complete(server.wait_closed())
    print('...server closed.')
    loop.close()


def main():
    """Command-line entry point for an experiment."""
    if not sys.argv[1:]:
        print('PLACE started: please use your keyboard')
        print('(or copy/paste) to input JSON experiment data...')
        _experiment_main(json.loads(sys.stdin.read()))
    elif len(sys.argv[1:]) == 2 and (sys.argv[1] == '-f' or sys.argv[1] == '--file'):
        with open(sys.argv[2]) as json_file:
            _experiment_main(json.load(json_file))
    elif len(sys.argv[1:]) == 1:
        _experiment_main(json.loads(sys.argv[1]))
    else:
        print("Usage: place_experiment '[JSON_STRING]'")
        print("       place_experiment -f [JSON_FILE]")
        print("       place_experiment --file [JSON_FILE]")
        print("       place_experiment < [JSON_FILE]")
        sys.exit(-1)

def web_main(args):
    """Web entry point for an experiment."""
    _experiment_main(json.loads(args))

def _experiment_main(config):
    BasicExperiment(config).run()
