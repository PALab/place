"""Starts the Django server"""
import os
import pkg_resources

from place.config import PlaceConfig

VERSION = pkg_resources.require("place")[0].version
INTRO = ("PLACE " + VERSION + " | Author: Paul Freeman | 2019\n" +
         "Originally created by: Jami L Johnson, Henrik tom Wörden, and Kasper van Wijk")


def main():
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


if __name__ == "__main__":
    main()
