"""The base mushroom class for moveable power-ups to inherit from."""

import pygame
import engine
from .. import Moveable

# The mushroom base class.
class MushroomBase(Moveable):
    # Construct a new mushroom base.
    def __init__(self, eng, classname):
        # Call the moveable constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("per_frame").hook(MushroomBase.eject)
        self.get_event("collision").hook(MushroomBase.player_collide)
        self.get_event("activated").set_func(MushroomBase.activated)
        self.movetype = engine.entity.MOVETYPE_CUSTOM

        # Cache the level object.
        self.level = None

        # Create a new event that is invoked when picked up by the player.
        self.set_event(engine.Event("pickup", lambda self, player: None))

        # Create an attribute for the origin of this power-up when activated.
        self.__origin = None

    # Initiate the ejection of this power-up.
    def activated(self):
        self.__origin = self.get_baseorigin()
        self.velocity.y = 64

    # Process the ejection of this power-up.
    def eject(self, name, returnValue):
        if (self.movetype == engine.entity.MOVETYPE_CUSTOM
            and self.get_baseorigin().y > self.__origin.y + self.get_hitbox().y):
            self.set_baseorigin(pygame.math.Vector2(
                self.__origin.x, self.__origin.y + self.get_hitbox().y))
            self.movetype = engine.entity.MOVETYPE_PHYSICS
        return engine.Event.DETOUR_CONTINUE

    # Handle acquiring the power-up by the player.
    def player_collide(self, name, returnValue, other, coltype, coldir):
        # If the other entity is not the player, continue.
        if other != self.level.player:
            return engine.Event.DETOUR_CONTINUE
        
        # If this entity is not manipulated by the physics engine, continue.
        if self.movetype != engine.entity.MOVETYPE_PHYSICS:
            return engine.Event.DETOUR_CONTINUE
        
        # Invoke the pickup event and delete this entity.
        self.invoke_event("pickup", self.level.player)
        self._engine.delete_entity(self)
        return (engine.Event.DETOUR_SUPERSEDE, False)