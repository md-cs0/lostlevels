"""A coin sprite which can either be part of the map or be released
out of power-up blocks."""

import pygame
import engine

# The coin class.
class Coin(engine.entity.Sprite):
    # Construct a new coin.
    def __init__(self, eng, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("collision").set_func(Coin.collision)
        self.movetype = engine.entity.MOVETYPE_ANCHORED
        
        # Load the coin spritesheet.
        self.load("lostlevels/assets/sprites/coin_big.png", (32, 32), 1)

        # Set some coin-specific properties.
        self.level = None
        self.collected = False
        self.coin_hit_sound = self._engine.create_sound("lostlevels/assets/audio/objects/coin_hit.ogg")
        self.coin_hit_sound.volume = 1

    # Increment the coins counter.
    def increment_counter(self):
        # Ensure that this has not been collected already.
        if self.collected:
            return

        # Increment the coins counter.
        self.level.get_save().header.m_sCoins += 1
        self.collected = True
        self.coin_hit_sound.play()

    # Handle collision with other entities.
    def collision(self, other, coltype, coldir):
        # If we collided with the player, increment the coins counter.
        if other == self.level.player:
            self.increment_counter()

        # If we hit the player, delete the coin.
        if other == self.level.player:
            self._engine.delete_entity(self)

        # Return false in all cases to prevent collision resolution.
        return False