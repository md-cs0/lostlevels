"""A basic sprite entity implementation, with physics operating by default.

Missing sprite sheets means the sprite texture will default to the missing 
texture image, which is 16x16 and will be stretched to compensate for the
tile size.
"""

import os
import pygame

from . import entity

# Macros.
SPRITES_PER_ROW = 16

# Cached sprite tiles.
cached_tiles = dict()

# Sprite entity.
class Sprite(entity.Entity):
    # Construct a new sprite.
    def __init__(self, engine, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(Sprite.draw_sprite)
        self.movetype = entity.MOVETYPE_PHYSICS

        # Texture information.
        self.__tiles = None
        self.__texture = None
        self.__flip_x = False
        self.__flip_y = False

        # Current tile index (which will wrap around).
        self.index = 0
        self.__oldindex = 0

    # Load from a tile sheet.
    def load(self, path, res, count):
        # Set the size of this sprite's hitbox.
        self.set_hitbox(pygame.math.Vector2(*res))

        # Fallback function, should the sheet provided be invalid.
        def fallback():
            nonlocal self, path
            self._engine.console.warn(f"tile sheet path \"{path}\" is invalid")
            self.__tiles = cached_tiles[path] = [pygame.transform.scale(self._engine.missing, res)]

        # Check whether the sheet is already cached.
        abspath = os.path.abspath(path)
        if abspath in cached_tiles:
            self.__tiles = cached_tiles[abspath]
        else:
            # Check if the path for the sheet exists.
            if not os.path.isfile(path):
                fallback()
                return
            
            # Attempt to load the image.
            try:
                sheet = pygame.image.load(path).convert_alpha()
                self.__tiles = cached_tiles[abspath] = []
            except pygame.error:
                fallback()
                return
            
            # Convert each tile into a separate surface object, and populate the
            # cached tiles array for this sheet.
            for i in range(0, count):
                # Calculate the row and column numbers with the current index.
                column = i % SPRITES_PER_ROW
                row = i // SPRITES_PER_ROW

                # Create a new surface for this tile specifically, and append it.
                tile = pygame.Surface(res, pygame.SRCALPHA)
                tile.blit(sheet, (0, 0), (column * res[0], row * res[1], *res))
                cached_tiles[abspath].append(tile)

    # Toggle which directions the sprite should flip in.
    def flip(self, flip_x = False, flip_y = False):
        if self.__flip_x != flip_x or self.__flip_y != flip_y:
            self.__texture = None
        self.__flip_x = flip_x
        self.__flip_y = flip_y

    # Draw this map tile entity.
    def draw_sprite(self, screen):
        # Re-render the texture if the index changed or if it is null.
        if not self.__texture or self.index != self.__oldindex:
            self.__oldindex = self.index
            self.__texture = pygame.Surface((self._rect.width, self._rect.height),
                                            pygame.SRCALPHA)
            self.__texture.blit(self.__tiles[self.index % len(self.__tiles)], (0, 0))
            if self.__flip_x or self.__flip_y:
                self.__texture = pygame.transform.flip(self.__texture, self.__flip_x, self.__flip_y)

        # Blit the current texture.
        screen.blit(self.__texture, self._rect)

    # Return how many tile entries are present for the loaded tileset.
    def get_tileset_count(self):
        return len(self.__tiles)