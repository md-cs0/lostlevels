"""A simple coloured rectangle, used with other UI elements."""

import pygame

from . import element

# Frame element.
class Frame(element.Element):
    # Construct a new frame.
    def __init__(self, engine, classname):
        # Call the element constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(Frame.draw_frame)

        # Rectangle properties.
        self.__colour = pygame.Color(0, 0, 0)
        self.__surface = None

    # Get the colour of this frame.
    def get_colour(self):
        return self.__colour

    # Set the colour of this frame.
    def set_colour(self, colour):
        self.__colour = colour
        self.__surface = None

    # Draw this frame.
    def draw_frame(self, screen):
        if not self.__surface:
            self.__surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
            self.__surface.fill(self.__colour)
        screen.blit(self.__surface, (self._rect.x, self._rect.y))