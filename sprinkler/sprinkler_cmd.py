"""
Created on 2024-08-13

@author: wf
"""

import sys
from argparse import ArgumentParser

from ngwidgets.cmd import WebserverCmd

from sprinkler.webserver import NiceSprinklerWebServer


class NiceSprinklerCmd(WebserverCmd):
    """
    command line handling for nicesprinkler
    """

    def __init__(self):
        """
        constructor
        """
        config = NiceSprinklerWebServer.get_config()
        WebserverCmd.__init__(self, config, NiceSprinklerWebServer, DEBUG)

    def getArgParser(self, description: str, version_msg) -> ArgumentParser:
        """
        override the default argparser call
        """
        parser = super().getArgParser(description, version_msg)
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="show verbose output [default: %(default)s]",
        )
        parser.add_argument(
            "--config",
            default="example_config.yaml",
            help="path to sprinkler configuration file [default: %(default)s]",
        )
        parser.add_argument(
            "--stl",
            default="example_garden.stl",
            help="path to sprinkler configuration file [default: %(default)s]",
        )
        return parser


def main(argv: list = None):
    """
    main call
    """
    cmd = NiceSprinklerCmd()
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
