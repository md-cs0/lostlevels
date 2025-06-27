"""This mushroom makes you jump high."""

import sys
import pygame
import engine

from . import MushroomBase
from .. import player

# The death cap class.
class DeathCap(MushroomBase):
    # Construct a new glitch power-up.
    def __init__(self, eng, classname):
        # Call the mushroom base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("pickup").set_func(DeathCap.pickup)
        self.speed = 75
        
        # Load the glitch power-up spritesheet.
        self.load("lostlevels/assets/sprites/death_cap.png", (32, 32), 1)

    # Pick up the death cap mushroom.
    def pickup(self, humanoid):
        if humanoid.get_class() == "player":
            humanoid.equip_powerup(player.POWERUP_DEATHCAP)
        self.powerup_sound.play()
        return True