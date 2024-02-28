#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Make a player entity with simple polygon artwork.

This will probably get broken up later when I make other polygon entities that
are not the player.

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

from pathlib import Path
import logging
import sys
import random
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"          # Set pygame env var to hide "Hello" msg
import pygame
logger = logging.getLogger(__name__)

class Points:
    """
    points: list of pygame.math.Vector2
    """
    def __init__(self, size:tuple, points:list):
        self.points = points
        self.size = size

    def copy_points(self) ->list:
        """Return a deep copy of self.points"""
        return [pygame.math.Vector2(point) for point in self.points]

class PolygonPlayer:
    """
    TODO: let size drive shape coordinates
    TODO: come up with better collision rect based on size
    """
    def __init__(self, game, pos, img_dur:int):
        self.game = game
        self.img_dur = img_dur
        # Store a basic shape which will then get animated with randomness.
        # TODO: store a collision size and a pygame.Surface size.
        size = (10,10)
        self.shape = Points(size,[
                pygame.math.Vector2(2,2), # top left
                pygame.math.Vector2(8,2), # top right
                pygame.math.Vector2(8,8), # bot right
                pygame.math.Vector2(5,6), # crotch
                pygame.math.Vector2(2,8), # bot left
                ])
        self.pos = list(pos)
        self.velocity = [0,0]
        self.collisions = {'top':False, 'bottom': False, 'right': False, 'left': False}

        # Update animation when frame % img_dur is 0
        self.frame = 0

    def rect(self):
        return pygame.Rect(*self.pos, *self.shape.size)

    def update(self, tilemap, movement=(0,0)) -> None:
        """Do the physics.

        - Calculate motion
        - Apply gravity
        - Check for collisions
        - Advance animation by one tick of the game loop
        - TODO: move randomized points with basic shape
        """
        # Reset collisions
        self.collisions = {'top':False, 'bottom': False, 'right': False, 'left': False}

        # Calculate motion
        frame_movement = (movement[0] + self.velocity[0], # x
                          movement[1] + self.velocity[1]) # y
        logger.debug(f"frame_movement: {frame_movement}")
        logger.debug(f"self.pos: {self.pos}, bottom: {self.rect().bottom}")

        # Update x position
        self.pos[0] += frame_movement[0]                # Update x

        # Check for x-collisions
        player_rect = self.rect()
        for rect in tilemap.rects_around(self.shape.size, self.pos):
            ### pygame.Rect.colliderect(Rect)
            if player_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    logger.debug("Collision: right")
                    player_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    logger.debug("Collision: left")
                    player_rect.left = rect.right
                    self.collisions['left'] = True
                # Record player x-position after collision.
                self.pos[0] = player_rect.x

        # Update y position
        self.pos[1] += frame_movement[1]                # Update y

        # Check for y-collisions
        player_rect = self.rect()
        ### rects_around(self, size, pos) -> list:
        for rect in tilemap.rects_around(self.shape.size, self.pos):
            ### pygame.Rect.colliderect(Rect)
            if player_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    logger.debug(f"Collision: bottom!\n\tPlayer bottom: {player_rect.bottom} collides with rect: {rect}, rect.top: {rect.top}.")
                    player_rect.bottom = rect.top
                    logger.debug(f"New player bottom: {player_rect.bottom}.")
                    self.collisions['bottom'] = True
                if frame_movement[1] < 0:
                    logger.debug("Collision: top!")
                    player_rect.top = rect.bottom
                    self.collisions['top'] = True
                # Record player y-position after collision.
                self.pos[1] = player_rect.y

        # Apply gravity with terminal velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Reset velocity if falling/rising stopped by a collision.
        if self.collisions['bottom'] or self.collisions['top']:
            self.velocity[1] = 0

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
        if 0: # Modify all points
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
