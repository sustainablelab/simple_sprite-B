#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""TODO: write a script docstring.
TODO: troubleshoot logging:
https://python.tutorialink.com/how-to-use-logging-getlogger__name__-in-multiple-modules/
"""
import sys
import pygame
import logging

# logger = logging.getLogger("tilemap")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
def what_tilemap_logger():
    """logger = logging.getLogger(__name__) """
    sys.exit(f"__name__: {__name__}, logger: {logger}")
    ### __name__: scripts.tilemap,
    ### logger: <Logger scripts.tilemap (WARNING)>

class Tilemap:
    def __init__(self, game, tile_size=4):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}

        # Manually code a few tiles
        # How many tiles fit on the game screen at once?
        tiles_x = self.game.game_art.get_width()//self.tile_size
        tiles_y = self.game.game_art.get_height()//self.tile_size
        # sys.exit(f"Screen fits tiles_x x tiles_y: {tiles_x} x {tiles_y}")
        ## Screen fits tiles_x x tiles_y: 40 x 22
        left_edge = -4
        right_edge = 4
        wall_height = 3
        for i in range(left_edge,right_edge+1):
            pos = (tiles_x//2 + i, tiles_y//2)
            self.tilemap[pos] = {'type': 'floor', 'pos':pos}
        for i in range(1,wall_height+1):
            # Left walls
            pos = (tiles_x//2 + left_edge, tiles_y//2 - i)
            self.tilemap[pos] = {'type': 'wall', 'pos':pos}
            # Right walls
            pos = (tiles_x//2 + right_edge, tiles_y//2 - i)
            self.tilemap[pos] = {'type': 'wall', 'pos':pos}

    def tiles_around(self, pos) -> list:
        """Return list of tiles near "pos"."""
        tiles = []
        # Get location of "pos" in tilemap grid coordinates
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        NEIGHBOR_OFFSETS = [ # the nine tiles near the player
                            (-1,-1),                            # bottom-left
                            ( 0,-1),                            # bottom-center
                            ( 1,-1),                            # bottom-right
                            (-1, 0),                            # middle-left
                            ( 0, 0),                            # middle-center
                            ( 1, 0),                            # middle-right
                            (-1, 1),                            # top-left
                            ( 0, 1),                            # top-center
                            ( 1, 1),                            # top-right
                           ]
        for offset in NEIGHBOR_OFFSETS:
            this_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
            if this_loc in self.tilemap:
                tiles.append(self.tilemap[this_loc])
        return tiles

    def rects_around(self, pos) -> list:
        """Return list of collision rects near "pos"."""
        rects = []
        neighbor_tiles = self.tiles_around(pos)
        for tile in neighbor_tiles:
            # sys.exit(f"tile: {tile}")
            rects.append(pygame.Rect(
                tile['pos'][0] * self.tile_size,
                tile['pos'][1] * self.tile_size,
                self.tile_size, self.tile_size))
        logger.debug(f"pos: {pos}, rects: {rects}")
        # if rects != []: logger.debug(f"pos: {pos}, rects: {rects}")
        ### pos: [160.0, 85.50000000000001],
        ### rects: [<rect(156, 88, 4, 4)>, <rect(160, 88, 4, 4)>, <rect(164, 88, 4, 4)>]
        return rects

    def render(self, surf, offset=(0,0)):
        """
        TODO: offset: camera motion in pixels
        """
        # Draw tile types
        # Floor tile
        floor_tile = pygame.Rect(0,0,self.tile_size,self.tile_size)
        floor_surf = pygame.Surface((self.tile_size,self.tile_size))
        pygame.draw.rect(floor_surf, (0,0,0), floor_tile)
        # Wall tile
        wall_tile = pygame.Rect(0,0,self.tile_size,self.tile_size)
        wall_surf = pygame.Surface((self.tile_size,self.tile_size))
        pygame.draw.rect(wall_surf, (50,50,50), wall_tile)
        # Look up tile in map and blit tile types
        # TODO: only blit tiles that are on visible screen
        for tile in self.tilemap:
            match self.tilemap[tile]['type']:
                case 'floor': tile_surf = floor_surf
                case 'wall': tile_surf = wall_surf
            surf.blit(tile_surf,
                      (tile[0]*self.tile_size,
                       tile[1]*self.tile_size))

