"""A flag which, upon touched, will cache the player's current position and
the level's time remaining, for the remainder of the player's session."""

import pygame
import engine

# The checkpoint class.
class Checkpoint(engine.entity.Sprite):
    # Construct a new checkpoint.
    def __init__(self, eng, classname):
        # Call the sprite constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("collision").set_func(Checkpoint.collision)
        self.movetype = engine.entity.MOVETYPE_ANCHORED

        # Load the coin spritesheet.
        self.load("lostlevels/assets/sprites/checkpoint.png", (41, 79), 2)

        # Store a reference to the current level scene.
        self.level = None

        # The index will be used to manage the state of the checkpoint.

    # If the player collides with the checkpoint while it has not been used,
    # cache the player's position and the level's time remaining. As nothing
    # should technically physically collide with the checkpoint itself,
    # this method always returns false.
    def collision(self, other, coltype, coldir):
        # If the other entity is not the player, continue.
        if other.get_class() != "player":
            return False
        
        # If the checkpoint has already been used, continue.
        if self.index == 1:
            return False
        
        # Use the checkpoint.
        player_offset = self.get_bottomleft() + pygame.math.Vector2(0, self.level.player.get_hitbox().y)
        self.level.set_checkpoint_data(player_offset)
        self._engine.console.log(f"Cached checkpoint at offset ({player_offset.x}, {player_offset.y}) " \
                                 f"and time limit {self.level.time_remaining:.0f}")
        self.index = 1
        return False