import pygame
import engine
import lostlevels

"""A bunch of sample functions that may be re-used for groups of elements."""

# collision: destroy objects hit by this entity.
def boulder_hit(self, other, coltype, coldir):
    # If this is not caused by the boulder itself, continue.
    if coltype != engine.entity.COLTYPE_COLLIDING:
        return
    
    # If the other entity is not within the player's viewpoint, continue.
    if other.get_absorigin().x > 576:
        return
    
    # Destroy the entity.
    self._engine.delete_entity(other)

# Rising platform: upon collision, configure the per_frame event.
def rise_on_collide(group):
    # Upon collision, hook each entity's per_frame event.
    for ent in group:
        ent.get_event("per_frame").hook(__rising_platform_per_frame)

# collisionfinal: upon collision, all of the elements part in the given group
# should become unanchored.
def unanchor_on_collide(eng, group, ent, other, coltype, coldir, allow_jumping = False):
    for member in group:
        if member.movetype != engine.entity.MOVETYPE_PHYSICS:
            member.movetype = engine.entity.MOVETYPE_PHYSICS
            if not allow_jumping:
                member.game_flags |= lostlevels.sprites.CANNOT_JUMP

# collisionfinal: upon collision with the player, all of the elements part in 
# the given group should become unanchored.
def unanchor_player_only(eng, group, ent, other, coltype, coldir, allow_jumping = False):
    if not other.get_class() == "player":
        return
    for member in group:
        if member.movetype != engine.entity.MOVETYPE_PHYSICS:
            member.movetype = engine.entity.MOVETYPE_PHYSICS
            if not allow_jumping:
                member.game_flags |= lostlevels.sprites.CANNOT_JUMP

# All methods below are for internal use only.

# Define the per-frame function for making each entity rise upwards. 
def __rising_platform_per_frame(self, name, returnValue):
    self.velocity.y += self._engine.find_gvar("gravity").get() * self._engine.globals.frametime
    return engine.Event.DETOUR_CONTINUE