#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Utilities.

"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def setup_logging(loglevel:str="WARNING",
                  detailed:bool=False,
                  log_file:Path=None) -> logging.Logger:
    """Set up logging to console and file.

    Only call this in game.py!

    Logging  replaces print() with logger.debug(), logger.info(), and
    logger.warning(). Use "loglevel" to control which messages print.

    "loglevel" and "detailed" are set by cmdline args. See "parse_cmdline_args".

    loglevel    Example: logging.debug, logging.info, logging.warning, etc.
    detailed    If False, prefix message with simple timestamp. If True,
                prefix message with lots of details. Available message details
                are listed below in "Excerpt from logging docs".

    Excerpt from logging docs
    -------------------------
    Formatter instances are used to convert a LogRecord to text.

    Formatters need to know how a LogRecord is constructed. They are
    responsible for converting a LogRecord to (usually) a string which can
    be interpreted by either a human or an external system. The base Formatter
    allows a formatting string to be specified. If none is supplied, the
    style-dependent default value, '%(message)s',  '{message}', or
    '${message}', is used.

    The Formatter can be initialized with a format string which makes use of
    knowledge of the LogRecord attributes - e.g. the default value mentioned
    above makes use of the fact that the user's message and arguments are pre-
    formatted into a LogRecord's message attribute. Currently, the useful
    attributes in a LogRecord are described by:

    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ( DEBUG ,  INFO ,
                         WARNING ,  ERROR ,  CRITICAL )
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
    """
    # Make the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # --Formatting--
    # Detail formatter includes lots of detail
    detail_formatter = logging.Formatter(
        fmt='%(asctime)s %(name)s %(levelname)s in \"%(funcName)s()\" at %(filename)s:%(lineno)d\n\t%(message)s',
        datefmt='%H:%M:%S')
    # Simple formatter is just timestamped messages.
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S')
    formatter = detail_formatter if detailed else simple_formatter
    if log_file:
        # ---Log to file---
        file_handler = logging.FileHandler(log_file, "w")# Write (do not append) log_file
        file_handler.setLevel(loglevel)                 # Set log level for file
        file_handler.setFormatter(formatter)            # Set log message formatting
        logger.addHandler(file_handler)                 # Add logging to file
    # --Log to console---
    console_handler = logging.StreamHandler()           # Make a stream handler
    console_handler.setLevel(loglevel)                  # Set log level for stream
    console_handler.setFormatter(formatter)             # Set log message formatting
    logger.addHandler(console_handler)                  # Add logging to console
    return logger

if __name__ == '__main__':
    print(f"Run doctests in {Path(__file__).name}")
    import doctest
    doctest.testmod()
