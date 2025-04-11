"""The Goomba enemy. It doesn't do much, except walk with a funny smile."""

import pygame
import engine
from . import EnemyBase

# The Goomba class.
class Goomba(EnemyBase):
    # Construct a new Goomba.
    def __init__(self, eng, classname):
        # Call the enemy base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.speed = 60
        
        # Load the Goomba power-up spritesheet.
        self.load("lostlevels/assets/sprites/goomba.png", (32, 26), 1)