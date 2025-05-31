import pygame
import engine
import lostlevels

"""A bunch of sample functions that may be re-used for groups of elements."""

# collisionfinal: upon collision, all of the elements part in the given group
# should become unanchored.
def unanchor_on_collide(eng, group, ent, other, coltype, coldir):
    for member in group:
        if member.movetype != engine.entity.MOVETYPE_PHYSICS:
            member.movetype = engine.entity.MOVETYPE_PHYSICS
            member.game_flags |= lostlevels.sprites.CANNOT_JUMP

# collisionfinal: upon collision with the player, all of the elements part in 
# the given group should become unanchored.
def unanchor_player_only(eng, group, ent, other, coltype, coldir):
    if not other.get_class() == "player":
        return
    for member in group:
        if member.movetype != engine.entity.MOVETYPE_PHYSICS:
            member.movetype = engine.entity.MOVETYPE_PHYSICS
            member.game_flags |= lostlevels.sprites.CANNOT_JUMP