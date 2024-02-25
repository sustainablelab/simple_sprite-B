#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""TODO: write a script docstring.
"""
import sys
import pygame

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
            self.tilemap[(tiles_x//2 + i, tiles_y//2)] = {'type': 'floor'}
        for i in range(1,wall_height+1):
            self.tilemap[(tiles_x//2 + left_edge, tiles_y//2 - i)] = {'type': 'wall'}
            self.tilemap[(tiles_x//2 + right_edge, tiles_y//2 - i)] = {'type': 'wall'}
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
        # Blit
        for tile in self.tilemap:
            match self.tilemap[tile]['type']:
                case 'floor': tile_surf = floor_surf
                case 'wall': tile_surf = wall_surf
            surf.blit(tile_surf,
                      (tile[0]*self.tile_size,
                       tile[1]*self.tile_size))

