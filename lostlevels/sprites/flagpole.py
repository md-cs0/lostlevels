"""The flagpole sprite is responsible for concluding a level.
Upon interaction, the player will progress to the next level."""

import pygame
import engine

from . import player

# The flagpole class.
class FlagPole(engine.entity.Sprite):
    # Construct a new flagpole.
    def __init__(self, eng, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("collision").set_func(FlagPole.collision)
        self.get_event("collisionfinal").set_func(FlagPole.collisionfinal)
        self.movetype = engine.entity.MOVETYPE_ANCHORED

        # Load the flagpole spritesheet.
        self.load("lostlevels/assets/sprites/flagpole.png", (12, 278), 2)

        # Troll toggle.
        self.troll = False

    # Handle general entity collision with the flagpole.
    def collision(self, other, coltype, coldir):
        # If the other entity is not the player entity, disable collision.
        if other.get_class() != "player":
            return False

        # If the player has already climbed a flagpole, disable collision.
        if other.climbed_flagpole:
            return False

        # Continue collision checks.
        return True

    # Handle the player interacting with the flagpole.
    def collisionfinal(self, other, coltype, coldir):
        # If the other entity is not the player entity, continue.
        if other.get_class() != "player":
            return

        # If this is a troll flagpole, make it so the flagpole can no longer
        # be interacted with but return immediately afterwards.
        if self.troll:
            self.movetype = engine.entity.MOVETYPE_NONE
            return

        # If the flagpole has already been used, continue.
        if self.movetype != engine.entity.MOVETYPE_ANCHORED:
            return
        
        # This flagpole is now being used; set the used flag and set the player's
        # climbing state, while hooking the player's collisionfinal event in order
        # to handle final collision so that the player can conclude climbing.
        self.movetype = engine.entity.MOVETYPE_NONE
        other.climbed_flagpole = True
        other.climb_velocity = -200
        other.set_climbing(self)
        other.get_event("collisionfinal").hook(handle_flagpole_collision)

# Call the player's Player::finish_level() method.
def handle_flagpole_collision(self, name, returnValue, other, coltype, coldir):
    self.finish_level()
    return engine.Event.DETOUR_CONTINUE