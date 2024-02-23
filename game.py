#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Experiment with sprite animation state machines."""

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"          # Set pygame env var to hide "Hello" msg
import pygame
import sys
import atexit
import logging
import argparse
from pathlib import Path
from scripts.utils import (
        setup_logging,
        )

def shutdown():
    """Clean up before exiting the game.

    This function runs before the program exits.
    Call "sys.exit()" to quit the program.
    """
    logger.debug("Shutdown")
    pygame.quit()

def parse_cmdline_args() -> argparse.Namespace:
    """Parse command line arguments.

        $ ./game.py -h
        pygame 2.1.3 (SDL 2.0.22, Python 3.10.12)
        Hello from the pygame community. https://www.pygame.org/contribute.html
        usage: game.py [-h] [-l {debug,info,warning}] [-d] [-s] [--windowed]

        options:
          -h, --help            show this help message and exit
          -l {debug,info,warning}, --log {debug,info,warning}
                                (dev) set console log level: --log=warning (default)
          -d, --detailed_log_prefix
                                (dev) use detailed log message prefix
          -s, --save_log_file   (dev) save log to file
          --windowed            (dev) start game in windowed mode
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-l", "--log", dest="loglevel",
            choices=["debug", "info", "warning"],
            default="warning",
            help="(dev) set console log level: --log=%(default)s (default)"
            )
    parser.add_argument(
            "-d", "--detailed_log_prefix", action="store_true",
            help="(dev) use detailed log message prefix"
            )
    parser.add_argument(
            "-s", "--save_log_file", action="store_true",
            help="(dev) save log to file"
            )
    parser.add_argument(
            "--windowed", action="store_true",
            help="(dev) start game in windowed mode"
            )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_cmdline_args()
    logger = setup_logging(
            loglevel=args.loglevel.upper(),
            detailed=args.detailed_log_prefix,
            log_file=Path(__file__).with_suffix(".log") if args.save_log_file else None
            )
    atexit.register(shutdown)
