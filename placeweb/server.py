"""Starts the Django server"""
import os
try:
    from importlib.metadata import version
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version

from place.config import PlaceConfig

try:
    VERSION = version("place")
except Exception:
    VERSION = "unknown"
INTRO = ("PLACE " + VERSION + " | Authors: Paul Freeman, Jonathan Simpson | 2023\n" +
         "Originally created by: Jami L Johnson, Henrik tom Wörden, and Kasper van Wijk")


def start():
    """Target for the `place_server` command"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "placeweb.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    config = PlaceConfig()
    ip_addr = config.get_config_value('Django', 'ip_address', '127.0.0.1')
    port = config.get_config_value('Django', 'port', '8000')
    address = '{}:{}'.format(ip_addr, port)
    print(INTRO)
    execute_from_command_line(['', 'runserver', address])
