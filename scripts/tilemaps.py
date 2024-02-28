#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""TODO: write a script docstring.
TODO: troubleshoot logging:
https://python.tutorialink.com/how-to-use-logging-getlogger__name__-in-multiple-modules/

    >>> a = [1, 2]
    >>> b = [3, 4]
    >>> a+b
    [1, 2, 3, 4]

    >>> int(10//10)
    1
    >>> int(10//4)
    2

    From numpy.ceil doc: The ceil of the scalar "x" is the smallest integer
    "i", such that "i >= x".
    >>> int(np.ceil(10/10))
    1
    >>> int(np.ceil(10/4))
    3
"""
import os
import sys
import pygame
import logging
import numpy as np

logger = logging.getLogger(__name__)

class Tilemap:
    def __init__(self, game, tile_size=8):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}

        # Manually code a few tiles
        # How many tiles fit on the game screen at once?
        tiles_x = self.game.game_art.get_width()//self.tile_size
        tiles_y = self.game.game_art.get_height()//self.tile_size
        # sys.exit(f"Screen fits tiles_x x tiles_y: {tiles_x} x {tiles_y}")
        ## Screen fits tiles_x x tiles_y: 40 x 22
        left_edge = -4                                  # 4 tiles left of platform center
        right_edge = 4                                  # 4 tiles right of platform center
        wall_height = 3                                 # walls are 3 tiles tall
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

    def tiles_around(self, size, pos) -> list:
        """Return list of tiles near an entity of some "size" at some "pos".

        Note if the entity size is larger than the tile size, there will be
        many tiles overlapping the entity.

        The tiles around the entity only touch a common center tile if the
        entity size and tile size are the same. That is the case in the
        DaFluffyPotato NINJA GAME tutorial.

        In my case, the entity size is larger than the tile size. How do I
        handle this?

        Say my tile size is 4x4 and my player size is 10x10. Here is what
        happens when the player falls onto a platform.

        t : tile
        o : tiles that overlap with player
        n : tiles that neighbor the player

        I draw my t, o, and n on screen as if this were "tile space" and I put
        the pixel y-coordinate next to each row of tile space.

        - On the left, I show where the platform is.
        - In the middle, I show the player location when initially colliding
          with the platform.
        - On the right, I show the player location when standing on the
          platform.

        Platform     Fall collision     On-platform collision
                                        76 n n n n n 
                     80 n n n n n       80 n o o o n 
                     84 n o o o n       84 n o o o n 
        88 t t t t   88 n o o o n       88 n o o o n 
                     92 n o o o n       92 n n n n n  <--- this row sees "on-platform"
                     96 n n n n n

        Keep in mind that when the player is bigger than the tiles, the
        "tile_loc" is the upper-left tile that overlaps the player. (The
        "tile_loc" is not the center tile!)

            tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))

        Since the tiles and player are square, the overlapping tiles form a
        square. I call this square the entity-size-in-tiles.

        I do not assume player size is a multiple of tile size. But entity-
        size-in-tiles must be a natural number. So I count a partial
        overlap of player and tile the same as a complete overlap.

        For example, in the picture above, the overlap is a 3x3 square:

            o o o
            o o o
            o o o

        10/4 = 2.5, not 3, but I round up to the nearest whole number.

        >>> int(np.ceil(10/4))
        3

        Say tile size is 5 instead of 4. Then 10/5 = 2. Since this is a whole
        number, the entity-size-in-tiles is only 2x2:

            o o
            o o

        Returning to the example, how do I automate this?
        First, I hardcode the o (overlap) and n (neighbor) tiles like this:

        OVERLAPPING_OFFSETS = [
                            (0, 0),                     # top-left
                            (0, 1),                     # top-center
                            (0, 2),                     # top-right
                            (1, 0),                     # mid-left
                            (1, 1),                     # center
                            (1, 2),                     # mid-right
                            (2, 0),                     # bot-left
                            (2, 1),                     # bot-center
                            (2, 2),                     # bot-right
                            ]
        NEIGHBOR_OFFSETS = [
                            (-1,-1),                    # top
                            ( 0,-1),                    # top
                            ( 1,-1),                    # top
                            ( 2,-1),                    # top

                            ( 3,-1),                    # right
                            ( 3, 0),                    # right
                            ( 3, 1),                    # right
                            ( 3, 2),                    # right

                            ( 0, 3),                    # bottom
                            ( 1, 3),                    # bottom
                            ( 2, 3),                    # bottom
                            ( 3, 3),                    # bottom

                            (-1, 0),                    # left
                            (-1, 1),                    # left
                            (-1, 2),                    # left
                            (-1, 3),                    # left
                           ]

        >>> e_size_in_tiles = int(np.ceil(10/4))
        >>> overlapping_offsets = []
        >>> offsets = tuple(range(0,e_size_in_tiles))
        >>> for xo in offsets:
        ...     for yo in offsets:
        ...         overlapping_offsets.append((xo,yo))
        >>> overlapping_offsets
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

        >>> neighbor_offsets = []
        >>> offsets = tuple(range(0,e_size_in_tiles+1))
        >>> for o in offsets:
        ...     neighbor_offsets.append((o, e_size_in_tiles)) # bottom
        ...     neighbor_offsets.append((o-1, -1))       # top
        ...     neighbor_offsets.append((e_size_in_tiles, o-1)) # right
        ...     neighbor_offsets.append((-1, o)) # left
        >>> neighbor_offsets
        [(0, 3), (-1, -1), (3, -1), (-1, 0),
         (1, 3), (0, -1),  (3, 0),  (-1, 1),
         (2, 3), (1, -1),  (3, 1),  (-1, 2),
         (3, 3), (2, -1),  (3, 2),  (-1, 3)]
        """
        tiles = []
        # Get location of "pos" in tilemap grid coordinates
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        # Get entity size in units of tiles
        e_size = size[0]                                # Assume player width = player height
        # Assume entity size >= tile size
        # If the entity size is not an exact multiple of the tile size, round up.
        e_size_in_tiles = int(np.ceil(e_size/self.tile_size))
        # List all tiles overlapping the player
        overlapping_offsets = []
        offsets = tuple(range(0,e_size_in_tiles))
        for xo in offsets:
            for yo in offsets:
                overlapping_offsets.append((xo,yo))
        # List all tiles that neighbor the player
        neighbor_offsets = []
        offsets = tuple(range(0,e_size_in_tiles+1))
        for o in offsets:
            neighbor_offsets.append((o, e_size_in_tiles)) # bottom
            neighbor_offsets.append((o-1, -1))            # top
            neighbor_offsets.append((e_size_in_tiles, o-1)) # right
            neighbor_offsets.append((-1, o))              # left
        for offset in (overlapping_offsets + neighbor_offsets):
            this_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
            if this_loc in self.tilemap:
                tiles.append(self.tilemap[this_loc])
        if tiles != []:
            logger.debug(f"tile_loc: {tile_loc}, "
                         f"e_size_in_tiles: {e_size_in_tiles}, "
                         f"tiles: {tiles}")
            ### tile_loc: (40, 20), e_size_in_tiles: 2.5,
            ### tiles: [{'type': 'floor', 'pos': (40, 22)},
            ###         {'type': 'floor', 'pos': (41, 22)},
            ###         {'type': 'floor', 'pos': (42, 22)},
            ###         {'type': 'floor', 'pos': (39, 22)}]
        return tiles

    def rects_around(self, size, pos) -> list:
        """Return list of collision rects near "pos"."""
        rects = []
        neighbor_tiles = self.tiles_around(size, pos)
        for tile in neighbor_tiles:
            # sys.exit(f"tile: {tile}")
            rects.append(pygame.Rect(
                tile['pos'][0] * self.tile_size,
                tile['pos'][1] * self.tile_size,
                self.tile_size, self.tile_size))
        # logger.debug(f"pos: {pos}, rects: {rects}")
        if rects != []: logger.debug(f"pos: {pos}, rects: {rects}")
        ### pos: [160.0, 80.1],
        ### rects: [<rect(160, 88, 4, 4)>,
        ###         <rect(164, 88, 4, 4)>,
        ###         <rect(168, 88, 4, 4)>,
        ###         <rect(156, 88, 4, 4)>]
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

if __name__ == '__main__':
    from pathlib import Path
    print(f"Run doctests in {Path(__file__).name}")
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
