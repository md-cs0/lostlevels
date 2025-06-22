"""An image element that is displayed to the end-user."""

import os
import pygame

from . import element

# Cached images.
cached_images = dict()

# Image element.
class Image(element.Element):
    # Construct a new image.
    def __init__(self, engine, classname):
        # Call the element constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(Image.draw_image)

        # Image properties.
        self.__image = None
        self.__texture = engine.missing # Default to the missing texture (although
                                        # it won't be stretched).

    # Pre-load an image.
    @staticmethod
    def preload(path):
        # Check whether the sheet is already cached.
        abspath = os.path.abspath(path)
        if abspath in cached_images:
            return cached_images[abspath]
        
        # Attempt to load the image.
        try:
            cached_images[abspath] = pygame.image.load(path).convert_alpha()
            return cached_images[abspath]
        except pygame.error:
            return None

    # Load from an image.
    def load(self, path):
        # Call the pre-load function.
        self.__image = Image.preload(path)
        if not self.__image:
            self._engine.console.warn(f"image path \"{path}\" is invalid")
            self.__image = self._engine.missing
            return
            
    # Upon setting the size of this image, re-scale the texture appropriately.
    def set_size(self, udim2, scale = True, offset = (0, 0)):
        super().set_size(udim2)
        res = (self._rect.width, self._rect.height)
        if scale:
            image = pygame.transform.scale(self.__image, res)
        else:
            image = self.__image
        self.__texture = pygame.Surface(res, pygame.SRCALPHA)
        self.__texture.blit(image, (0, 0), (*offset, *res))

    # Flip this image.
    def flip(self, flip_x = False, flip_y = False):
        self.__texture = pygame.transform.flip(self.__texture, flip_x, flip_y)

    # Draw this frame.
    def draw_image(self, screen):
        screen.blit(self.__texture, self._rect)