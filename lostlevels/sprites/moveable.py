"""A moveable, such as a power-up mushroom or an enemy target."""

import pygame
import engine

# The moveable class.
class Moveable(engine.entity.Sprite):
    # Construct a new moveable.
    def __init__(self, engine, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("per_frame").set_func(Moveable.per_frame)
        self.get_event("collisionfinal").set_func(Moveable.collisionfinal)
        self.acceleration = 10000   # Accelerate instantly.

        # Create some attributes for controlling the moveable.
        self.speed = 0              # Modify this instead of move.
        self.negate_speed = False   # If true, move leftwards instead of rightwards.

    # Control the moveable's move.
    def per_frame(self):
        self.move = -self.speed if self.negate_speed else self.speed
        self.flip(self.negate_speed)

    # Handle colliding with walls.
    def collisionfinal(self, other, coltype, coldir):
        # If this moveable was moving to the left and collided with a wall
        # to the left of it, change directions.
        if ((coltype == engine.entity.COLTYPE_COLLIDING and coldir == engine.entity.COLDIR_RIGHT)
            or (coltype == engine.entity.COLTYPE_COLLIDED and coldir == engine.entity.COLDIR_LEFT)
            and self.negate_speed):
            self.negate_speed = not self.negate_speed

        # If this moveable was moving to the right and collided with a wall
        # to the right of it, change directions.
        elif ((coltype == engine.entity.COLTYPE_COLLIDING and coldir == engine.entity.COLDIR_LEFT)
            or (coltype == engine.entity.COLTYPE_COLLIDED and coldir == engine.entity.COLDIR_RIGHT)
            and not self.negate_speed):
            self.negate_speed = not self.negate_speed