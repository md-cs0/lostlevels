"""A basic entity consisting of a map tile, loaded from a tile sheet.

Missing tile sheets means the tile texture will default to a missing texture
image, which is 16x16 and will be stretched to compensate for the tile size."""

import os
import pygame

from . import entity

# Macros.
TILES_PER_ROW = 16

# Cached tile sheets.
cached_sheets = dict()

# Map tile entity.
class Tile(entity.Entity):
    # Construct a new map tile.
    def __init__(self, engine, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(Tile.draw_tile)
        self.movetype = entity.MOVETYPE_ANCHORED

        # Map tile properties.
        self.__texture = engine.missing # Default to the missing texture (although
                                        # it won't be stretched).

    # Load from a tile sheet.
    def load(self, path, res, index):
        # Set the size of this tile's hitbox.
        self.set_hitbox(pygame.math.Vector2(*res))

        # Fallback function, should the sheet provided be invalid.
        def fallback():
            nonlocal self, path
            self._engine.console.warn(f"tile sheet path \"{path}\" is invalid")
            self.__texture = pygame.transform.scale(self._engine.missing, res)

        # Check whether the sheet is already cached.
        abspath = os.path.abspath(path)
        if abspath in cached_sheets:
            sheet = cached_sheets[abspath]
        else:
            # Check if the path for the sheet exists.
            if not os.path.isfile(path):
                fallback()
                return

            # Attempt to load the image.
            try:
                sheet = cached_sheets[abspath] = pygame.image.load(path).convert_alpha()
            except pygame.error:
                fallback()
                return
        
        # Calculate the row and column numbers with the index provided.
        column = index % TILES_PER_ROW
        row = index // TILES_PER_ROW
        
        # Create a new surface for this tile specifically.
        self.__texture = pygame.Surface(res, pygame.SRCALPHA)
        self.__texture.blit(sheet, (0, 0), (column * res[0], row * res[1], *res))

    # Flip this tile.
    def flip(self, flip_x = False, flip_y = False):
        self.__texture = pygame.transform.flip(self.__texture, flip_x, flip_y)

    # Rotate this tile. Note that the hitbox size will not change!
    def rotate(self, angle):
        self.__texture = pygame.transform.rotate(self.__texture, angle)

    # Draw this map tile entity.
    def draw_tile(self, screen):
        screen.blit(self.__texture, self._rect)