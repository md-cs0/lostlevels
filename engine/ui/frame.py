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
        self.colour = pygame.Color(0, 0, 0)

    # Draw this frame.
    def draw_frame(self, screen):
        pygame.draw.rect(screen, self.colour, self._rect)