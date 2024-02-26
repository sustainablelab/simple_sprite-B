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
        PolygonPlayer,
        what_utils_logger,
        )
from scripts.tilemap import (
        Tilemap,
        what_tilemap_logger,
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

class Game:
    def __init__(self, windowed):
        pygame.init()

        # TODO: create classes OsWindow and GameScreen to organize this data.
        # Use the --windowed cmdline arg
        self.is_fullscreen = not windowed

        # OS window
        pygame.display.set_caption("Experiment with Sprite Animations")
        os.environ["PYGAME_BLEND_ALPHA_SDL2"] = "1"     # Use SDL2 alpha blending
        os.environ["SDL_VIDEO_WINDOW_POS"] = "800,0"
        ### Surface((width, height), flags=0, depth=0, masks=None) -> Surface
        self.game_art = pygame.Surface(
                # (16*40,9*40),                           # 640x360x32
                # (16*30,9*30),                           # 480x270x32
                (16*20,9*20),                           # 320x180x32
                flags=0,                                # Example flag: pygame.SRCALPHA
                )
        logger.debug(f"self.game_art: {self.game_art}")
        self.render_scale = 2
        # Screen size is the portion of the screen that is filled with game art.
        # Initial windowed size is hardcoded to be 2 * game_art size
        self.windowed_size = (int(self.game_art.get_width()*self.render_scale),
                              int(self.game_art.get_height()*self.render_scale))
        logger.debug(f"self.windowed_size: {self.windowed_size}")
        self.screen_flags = pygame.RESIZABLE
        if self.is_fullscreen:
            self.screen_flags |= pygame.FULLSCREEN
        self.os_window = None
        self.screen_size = None
        self.screen_offset = None
        self.get_new_os_window( # Updates self.os_window, self.screen_size, self.screen_offset
                self.is_fullscreen,
                self.windowed_size,
                self.screen_flags
                )

        self.tilemap = Tilemap(self)

        self.polygon_player = PolygonPlayer(self,
                                            pos=(self.game_art.get_width()/2, 0),
                                            img_dur=6)
        self.movement = [False, False]                  # [Left, Right]

        # FPS
        self.clock = pygame.time.Clock()

        self.windowed = windowed

    def run(self):
        while True: self.game_loop()

    def game_loop(self):
        # Set game background color
        bgnd_color = pygame.color.Color(100,100,100)
        self.game_art.fill(bgnd_color)

        self.tilemap.render(self.game_art)

        # Draw a square
        self.polygon_player.update(
                # Use tilemap for collision detection
                self.tilemap,
                # X movement: (1-0) RIGHT | (0-1) LEFT | (0) BOTH/NONE
                (self.movement[1] - self.movement[0], 0)
                )
        self.polygon_player.render()

        self.handle_ui_events()

        # Clear the OS_window to black
        self.os_window.fill((0,0,0))
        # Size, position, and draw the game screen in the OS window
        self.os_window.blit(pygame.transform.scale(self.game_art, self.screen_size), self.screen_offset)
        # Draw to the OS Window
        pygame.display.update()

        ### clock.tick(framerate=0) -> milliseconds
        self.clock.tick(60)

    def handle_ui_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.WINDOWRESIZED:
                    if not self.is_fullscreen:
                        self.windowed_size = (event.x, event.y)
                        logger.debug(f"self.windowed_size: {self.windowed_size:}")
                        self.screen_size = self.windowed_size
                        self.update_screen()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE | pygame.K_q: sys.exit()
                        case pygame.K_F11:
                            self.is_fullscreen = not self.is_fullscreen
                            if self.is_fullscreen:
                                # Set FULLSCREEN flag
                                self.screen_flags |= pygame.FULLSCREEN
                            else:
                                # Clear FULLSCREEN flag
                                self.screen_flags &= ~pygame.FULLSCREEN
                            self.get_new_os_window(
                                    self.is_fullscreen,
                                    self.windowed_size,
                                    self.screen_flags)
                        case pygame.K_h | pygame.K_a | pygame.K_LEFT:
                            self.movement[0] = True
                        case pygame.K_l | pygame.K_d | pygame.K_RIGHT:
                            self.movement[1] = True
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_h | pygame.K_a | pygame.K_LEFT:
                            self.movement[0] = False
                        case pygame.K_l | pygame.K_d | pygame.K_RIGHT:
                            self.movement[1] = False

    def get_new_os_window(self, is_fullscreen:bool, windowed_size:tuple, screen_flags:int) -> None:
        """Get a new OS window when the OS window switches between windowed and fullscreen.

        Context: pressing F11 toggles fullscreen by setting/clearing the
        self.screen_flags and calling "get_new_os_window".

        Updates
        -------
        self.os_window
        self.screen_size
        """
        if is_fullscreen:
            logger.info("FULLSCREEN")
            # Get desktop size (size of full screen)
            # TODO: handle case where there are multiple displays
            desktop_sizes = pygame.display.get_desktop_sizes()
            logger.debug(f"pygame.display.get_desktop_sizes(): {desktop_sizes}")
            ### Framework laptop: pygame.display.get_desktop_sizes(): [(1496, 1002)]
            self.screen_size = desktop_sizes[0]
        else:
            logger.info("WINDOWED")
            self.screen_size = windowed_size
        logger.info(f"self.screen_size: {self.screen_size}")
        self.update_screen()
        # Apply updated screen size and flags
        # (If full screen, screen size doesn't matter here, but will matter
        # later when blitting).
        self.os_window = pygame.display.set_mode(self.screen_size, screen_flags)
        logger.debug(f"self.os_window: {self.os_window}")

    def update_screen(self) -> None:
        """Recalculate screen size and position after window size changes.

        Window size can change either by going fullscreen or by the user
        click-dragging the window border.

        Recalculate to maintain game art aspect ratio and keep screen centered
        in OS window.

        Updates
        -------
        self.render_scale
        self.screen_size
        self.screen_offset
        """
        new_window_size = self.screen_size
        # Calculate the render_scale
        self.render_scale = min(new_window_size[0]/self.game_art.get_width(),
                                new_window_size[1]/self.game_art.get_height()
                                )
        logger.debug(f"self.render_scale: {self.render_scale}")
        # Calculate new screen size (largest screen that fits in new window
        # whilst preserving game art aspect ratio)
        self.screen_size = (int(self.game_art.get_width()*self.render_scale),
                            int(self.game_art.get_height()*self.render_scale))
        # Calculate new screen offset in OS window
        self.screen_offset = (
                (new_window_size[0] - self.screen_size[0])//2,
                (new_window_size[1] - self.screen_size[1])//2)
        logger.debug(f"self.screen_offset: {self.screen_offset}")

if __name__ == '__main__':
    args = parse_cmdline_args()
    logger = setup_logging(
            loglevel=args.loglevel.upper(),
            detailed=args.detailed_log_prefix,
            log_file=Path(__file__).with_suffix(".log") if args.save_log_file else None
            )
    atexit.register(shutdown)
    # what_utils_logger()
    # what_tilemap_logger()
    Game(args.windowed).run()
