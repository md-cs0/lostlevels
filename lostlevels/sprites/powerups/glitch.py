"""A Glitch Productions special."""

import sys
import pygame
import engine
from . import MushroomBase

# The glitch power-up class.
class GlitchPowerup(MushroomBase):
    # Construct a new glitch power-up.
    def __init__(self, eng, classname):
        # Call the mushroom base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("pickup").set_func(GlitchPowerup.pickup)
        self.speed = 75
        
        # Load the glitch power-up spritesheet.
        self.load("lostlevels/assets/sprites/glitched_powerup.png", (32, 32), 1)

    # Create an error screen and shut down the game.
    def pickup(self, player):
        # Stop the music and stop the player from being able to move.
        self.level.stop_music()
        player.moveable = False
        player.move = 0

        # Create the fake error screen.
        error = self._engine.create_ui_element_by_class("image")
        error.load("lostlevels/assets/error.png")
        error.set_size(engine.ui.UDim2(1, 0, 1, 0))
        error.enabled = True

        # Play the Nintendo GameCube piano error sound.
        error_sound = self._engine.create_sound("lostlevels/assets/audio/objects/glitch_powerup.ogg")
        error_sound.volume = 1
        error_sound.play()
        
        # Create an engine timer for shutting down the game in 2 seconds.
        self._engine.create_timer(lambda: sys.exit(1), 2)