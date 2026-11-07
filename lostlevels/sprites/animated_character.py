"""An animated character sprite that must be moved programmatically.
At the moment, only idling and walking is animated:
- Idling: index 0
- Walking: indexes 1-3"""

import time
import pygame
import engine
import lostlevels

from . import Humanoid

# The animated character class.
class AnimatedCharacter(engine.entity.Sprite, Humanoid):
    # Construct a new animated character.
    def __init__(self, eng, classname):
        # Call the sprite constructor and modify its default properties.
        engine.entity.Sprite.__init__(self, eng, classname)
        Humanoid.__init__(self)
        self.get_event("per_frame").set_func(AnimatedCharacter.per_frame)
        self.acceleration = 6.5

        # Toggle whether the character should be animated.
        self.animate = True

        # Store the timestamp for when the character's animation last changed.
        self.__animtimestamp = 0

    # Handle player movement per-frame.
    def per_frame(self):
        # Should this player be animated automatically?
        if self.animate:
            # Flip the player sprite in the direction of travel.
            if abs(self.velocity.x) > 0.1:
                self.flip(self.velocity.x < 0)
            
            # Animate the player based on its current movement.
            if abs(self.velocity.x) > 0.1:
                length = max(1 / (abs(self.velocity.x) / 20), 1 / 60)
                if time.perf_counter() > self.__animtimestamp + length:
                    self.__animtimestamp = time.perf_counter()
                    self.index = (self.index % 3) + 1
            else:
                self.index = 0