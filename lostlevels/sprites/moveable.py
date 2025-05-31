"""A moveable, such as a power-up mushroom or an enemy target."""

import pygame
import engine

# The moveable class.
class Moveable(engine.entity.Sprite):
    # Construct a new moveable.
    def __init__(self, engine, classname):
        # Call the sprite constructor and modify its default properties.
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
        if engine.entity.is_collision_leftwards(coltype, coldir) and self.negate_speed:
            self.negate_speed = not self.negate_speed

        # If this moveable was moving to the right and collided with a wall
        # to the right of it, change directions.
        elif engine.entity.is_collision_rightwards(coltype, coldir) and not self.negate_speed:
            self.negate_speed = not self.negate_speed

        # Otherwise, do not evaluate anything.
        else:
            return

        # If the other entity is a moveable, set its negate_speed attribute to
        # be the opposite of this moveable's negate_speed.
        if isinstance(other, Moveable):
            other.negate_speed = not self.negate_speed