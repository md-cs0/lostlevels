"""Lost Levels power-up block sprite."""

import pygame
import engine
import lostlevels.sprites

# The power-up block class.
class PowerupBlock(engine.entity.Sprite):
    # Construct a new power-up block.
    def __init__(self, eng, classname):
        # Call the sprite constructor and modify its default properties.
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
        self.released = False
        self.biome = ""

        # Create new events that are called when the power-up block is hit.
        self.set_event(engine.Event("release", PowerupBlock.release))    # Called immediately after being hit.
        self.set_event(engine.Event("release_fixed", lambda self: None)) # Called when the block gets fixed.

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
        return (coldir == engine.entity.COLDIR_DOWN and other.get_class() == "player"
                and other.get_baseorigin().y < self.get_baseorigin().y)

    # Unanchor the power-up block briefly to move it slightly.
    def unanchor(self, name, returnValue, other, coltype, coldir):
        # Check if this power-up block should be triggered.
        if not self.__should_trigger(other, coltype, coldir):
            return engine.Event.DETOUR_CONTINUE
        
        # If this entity has already been hit, continue.
        if self.hit:
            return engine.Event.DETOUR_CONTINUE
        
        # If this entity has not been unanchored, move it now.
        if self.origin_y == None:
            # First, check for whether there actually is space to move.
            origin = self.get_baseorigin()
            query = self._engine.query_entities(
                origin, origin + pygame.math.Vector2(32, 1), False)
            for ent in query:
                # If this entity is the power-up block itself, continue.
                if ent == self:
                    continue

                # Skip invisible entities as well.
                if not ent.draw:
                    continue

                # If this is an enemy target, kill it and continue.
                # Before you wonder: yes, it is intentional that destructible
                # blocks do not kill enemies.
                if isinstance(ent, lostlevels.sprites.enemies.EnemyBase):
                    ent.invoke_event("kill")
                    continue

                # Don't sent the power-up block upwards. If the block
                # is meant to free-fall, release it anyway. Otherwise,
                # call the release_fixed event and exit.
                if self.fall:
                    self.movetype = engine.entity.MOVETYPE_PHYSICS
                else:
                    self.invoke_event("release_fixed")
                return engine.Event.DETOUR_CONTINUE

            # Release the power-up block.
            self.movetype = engine.entity.MOVETYPE_PHYSICS
            self.velocity.y = 200
            self.origin_y = self.get_baseorigin().y

        # Continue.
        return engine.Event.DETOUR_CONTINUE
    
    # Reset this block upon being hit and call the release event.
    def hit(self, other, coltype, coldir):
        # Check if this entity has not been hit already.
        if not self.hit:
            # Check if this power-up block should be triggered.
            if not self.__should_trigger(other, coltype, coldir):
                return
            
            # Reset this block and call the release event.
            self.index = 4
            self.hit = True
            self.draw = True
            self.invoke_event("release")

        # Otherwise, check if it hasn't released a power-up when in free-fall.
        elif not self.released and self.fall:
            # If it didn't collide with an entity below, continue.
            if not engine.entity.is_collision_below(coltype, coldir):
                return
            
            # Release the power-up after fixing itself.
            self.invoke_event("release_fixed")
            self.released = True

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
            self.invoke_event("release_fixed")
            self.released = True

    # Should this power-up block be triggered?
    def __should_trigger(self, other, coltype, coldir):
        # Check if this is a player hitting from underneath.
        if other.get_class() == "player" and coldir == engine.entity.COLDIR_DOWN:
            return True
        
        # Check if this is a Koopa hitting from the side.
        if (other.get_class() == "koopa" and other.kicked and
            (coldir == engine.entity.COLDIR_LEFT or coldir == engine.entity.COLDIR_RIGHT)):
            return True
        
        # Otherwise, return false.
        return False