#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Utilities.

random examples
---------------

    >>> 0 < random.random() < 1
    True
    >>> type(random.random())
    <class 'float'>

    >>> 1<<16
    65536
    >>> 0 < random.random()*(1<<16) < 1<<16
    True
    >>> type(random.random()*(1<<16))
    <class 'float'>

    >>> list(range(0,2))
    [0, 1]
    >>> 0 < random.choice(list(range(1<<16))) < 1<<16
    True
    >>> type(random.choice(list(range(1<<16))))
    <class 'int'>

    >>> -1 < random.uniform(-1,1) < 1
    True
    >>> type(random.uniform(-1,1))
    <class 'float'>
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"          # Set pygame env var to hide "Hello" msg
import pygame
from pathlib import Path
import logging
import sys
import random

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
    logger = logging.getLogger(__name__)
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

class Points:
    """
    points: list of pygame.math.Vector2
    """
    def __init__(self, points:list):
        self.points = points

    def copy_points(self) ->list:
        """Return a deep copy of self.points"""
        return [pygame.math.Vector2(point) for point in self.points]

class PolygonPlayer:
    def __init__(self, game, pos, img_dur:int):
        self.game = game
        self.img_dur = img_dur
        # Store a basic shape which will then get animated with randomness.
        self.shape = Points([
                pygame.math.Vector2(2,2), # top left
                pygame.math.Vector2(8,2), # top right
                pygame.math.Vector2(8,8), # bot right
                pygame.math.Vector2(5,6), # crotch
                pygame.math.Vector2(2,8), # bot left
                ])
        self.pos = list(pos)
        self.velocity = [0,0]

        # Update animation when frame % img_dur is 0
        self.frame = 0

    def update(self, movement=(0,0)) -> None:
        """Do the physics.

        - Calculate motion
        - Apply gravity
        - TODO: check for collisions
        - Advance animation by one tick of the game loop
        """
        # Calculate motion
        frame_movement = (movement[0] + self.velocity[0], # x
                          movement[1] + self.velocity[1]) # y
        # Update position
        self.pos[0] += frame_movement[0]                # Update x
        self.pos[1] += frame_movement[1]                # Update y

        # Apply gravity with terminal velocity
        self.velocity[1] = min(3, self.velocity[1] + 0.1)

        # Animation
        if self.frame == 0:
            # Update how you look
            self.animate_points()
        self.frame = (self.frame+1) % self.img_dur

    def animate_points(self) -> None:
        # TODO: add animation here
        # For now, I am just adding randomness to the shape.
        # Copy shape to a new list of points
        self.points = self.shape.copy_points()
        if 0: # Example of modifying a single point
            self.points[0][0] += random.choice(list(range(-1,1+1)))
            self.points[0][1] += random.choice(list(range(-1,1+1)))
        if 1: # Modify all points
            for point in self.points:
                point[0] += random.choice(list(range(-1,1+1)))
                point[1] += random.choice(list(range(-1,1+1)))
    def render(self) -> None:
        use_alpha = True
        use_add = not use_alpha
        if use_alpha:
            flag = pygame.BLEND_ALPHA_SDL2
            polygon_color_shape = pygame.color.Color(20,20,20)
            polygon_color_effect = pygame.color.Color(20,20,20,100)
        if use_add:
            flag = pygame.BLEND_ADD
            polygon_color_shape = pygame.color.Color(40,40,40)
            polygon_color_effect = pygame.color.Color(40,40,40)

        if use_alpha: # Only show base shape while debugging
            draw_shape = True
            draw_effect = False
        if use_add: # Show both shapes: the add makes the basic shape look dynamic
            draw_shape = True
            draw_effect = True
        if draw_shape:
            polygon_surf = pygame.Surface((10,10), pygame.SRCALPHA)
            ### pygame.draw.polygon(surface, color, points, width=0) -> Rect
            pygame.draw.polygon(polygon_surf, polygon_color_shape, self.shape.points)
            ### Surface.blit(source, dest, area=None, special_flags=0) -> Rect
            self.game.game_art.blit(polygon_surf, self.pos, special_flags=flag)
        if draw_effect:
            polygon_surf = pygame.Surface((10,10), pygame.SRCALPHA)
            ### pygame.draw.polygon(surface, color, points, width=0) -> Rect
            pygame.draw.polygon(polygon_surf, polygon_color_effect, self.points)
            ### Surface.blit(source, dest, area=None, special_flags=0) -> Rect
            self.game.game_art.blit(polygon_surf,
                                    (self.game.game_art.get_width()/2, 10),
                                    special_flags=flag)

if __name__ == '__main__':
    print(f"Run doctests in {Path(__file__).name}")
    import doctest
    doctest.testmod()
