"""A basic entity consisting of a rectangle, of any colour and size!"""

import pygame

from . import entity

# Rectangle entity.
class Rectangle(entity.Entity):
    # Construct a new rectangle.
    def __init__(self, engine, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(draw_rectangle)
        self.movetype = entity.MOVETYPE_ANCHORED

        # Rectangle properties.
        self.colour = pygame.Color(0, 0, 0)

# Draw this rectangle.
def draw_rectangle(self, screen):
    pygame.draw.rect(screen, self.colour, self._rect)