"""Lost Levels power-up block sprite."""

import pygame
import engine

# The power-up block class.
class PowerupBlock(engine.entity.Sprite):
    # Construct a new power-up block.
    def __init__(self, eng, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("activated").set_func(PowerupBlock.activated)
        self.get_event("collision").set_func(PowerupBlock.collision)
        self.get_event("collisionfinal").hook(PowerupBlock.unanchor)
        self.get_event("collisionfinal").set_func(PowerupBlock.hit)
        self.get_event("per_frame").set_func(PowerupBlock.per_frame)
        self.movetype = engine.entity.MOVETYPE_ANCHORED

        # Power-up block properties.
        self.fall = False
        self.hit = False
        self.origin_y = None
        self.level = None
        self.decoy = False
        self.biome = ""

        # Create an event that is called when the power-up block is hit.
        self.set_event(engine.Event("release", PowerupBlock.release))

    # Set the index of this power-up block.
    def activated(self):
        self.load(f"lostlevels/assets/biomes/{self.biome}/powerup_box.png", (32, 32), 10)
        if self.decoy:
            self.index = 5
        else:
            self._engine.create_timer(self.scroll_powerup, 0.1)

    # Scroll the question mark.
    def scroll_powerup(self):
        if not self.hit:
            self.index = (self.index + 1) % 4
            self._engine.create_timer(self.scroll_powerup, 0.1)

    # If this block is invisible, handle collision.
    def collision(self, other, coltype, coldir):
        # If this block is visible, return true in all cases.
        if self.draw:
            return True
        
        # Otherwise, only return true if this is a player hitting from below.
        return (coldir == engine.entity.COLDIR_DOWN and other == self.level.player
                and other.get_baseorigin().y < self.get_baseorigin().y)

    # Unanchor the power-up block briefly to move it slightly.
    def unanchor(self, name, returnValue, other, coltype, coldir):
        # If the other entity is not the player, continue.
        if other != self.level.player:
            return engine.Event.DETOUR_CONTINUE

        # If this entity was not hit from below, continue.
        if coldir != engine.entity.COLDIR_DOWN:
            return engine.Event.DETOUR_CONTINUE
        
        # If this entity has already been hit, continue.
        if self.hit:
            return engine.Event.DETOUR_CONTINUE
        
        # If this entity has not been unanchored, move it now.
        if self.origin_y == None:
            self.movetype = engine.entity.MOVETYPE_PHYSICS
            self.velocity.y = 200
            self.origin_y = self.get_baseorigin().y

        # Continue.
        return engine.Event.DETOUR_CONTINUE
    
    # Reset this block upon being hit and call the release event.
    def hit(self, other, coltype, coldir):
        # If the other entity is not the player, continue.
        if other != self.level.player:
            return

        # If this entity was not from below, continue.
        if coldir != engine.entity.COLDIR_DOWN:
            return

        # If this entity has already been hit, continue.
        if self.hit:
            return
        
        # Reset this block and call the release event.
        self.index = 4
        self.hit = True
        self.draw = True
        self.invoke_event("release")

    # Release a coin from this block by default:
    def release(self):
        coin = self._engine.create_entity_by_class("coin")
        coin.level = self.level
        coin.increment_counter()
        coin.set_baseorigin(self.get_baseorigin() + pygame.math.Vector2(0, 32))
        coin.movetype = engine.entity.MOVETYPE_PHYSICS
        coin.velocity = pygame.math.Vector2(0, 500)
        self._engine.activate_entity(coin)

    # Handle falling the entity back into its original place.
    def per_frame(self):
        origin = self.get_baseorigin()
        if (not self.fall and self.movetype == engine.entity.MOVETYPE_PHYSICS 
            and origin.y < self.origin_y):
            self.movetype = engine.entity.MOVETYPE_ANCHORED
            self.set_baseorigin(pygame.math.Vector2(origin.x, self.origin_y))