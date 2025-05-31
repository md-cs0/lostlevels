"""The Koopa enemy. They can be forced into their shells and kicked into other enemies."""

import time
import pygame
import engine
from . import EnemyBase

# The Koopa class.
class Koopa(EnemyBase):
    # Construct a new Koopa.
    def __init__(self, eng, classname):
        # Call the enemy base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("activated").set_func(Koopa.animate)
        self.get_event("player_hit").set_func(Koopa.player_hit)
        self.get_event("collision").set_func(Koopa.collision)
        self.get_event("collisionfinal").hook(Koopa.collisionfinal)
        self.get_event("collisionfinal").remove_hook(EnemyBase.player_collide)
        self.speed = 60
        
        # Load the Koopa power-up spritesheet.
        self.load("lostlevels/assets/sprites/koopa.png", (31, 48), 3)

        # Handle the Koopa in its shell form.
        self.stomped = False
        self.kicked = False
        self.time_since_hit = time.perf_counter()

        # Store some Koopa-specific sounds.
        self.block_hit_sound = self._engine.create_sound("lostlevels/assets/audio/player/block_hit.ogg")
        self.block_hit_sound.volume = 1

    # Animate this Koopa while it still hasn't been stomped.
    def animate(self):
        if not self.stomped:
            self.index = (self.index + 1) % 2
            self._engine.create_timer(self.animate, 0.25)

    # Handle stomping the Koopa.
    def player_hit(self, player):
        # If this Koopa has not been stomped, stomp it into its shell.
        if not self.stomped:
            self._engine.console.log(f"[Lost Levels]: enemy \"{self.get_class()}\" was stomped into shell")
            self.index = 2
            self.speed = 0
            self.set_hitbox(pygame.math.Vector2(25, 24))
            self.set_baseorigin(self.get_baseorigin() - pygame.math.Vector2(0, 24))
            self.stomped = True
            self.stomp.play()
            self.level.get_save().header.m_uScore += 100

        # Otherwise, this Koopa is probably being kicked. Stop it from moving.
        elif self.kicked:
            self._engine.console.log(f"[Lost Levels]: enemy \"{self.get_class()}\" was stomped into shell")
            self.kicked = False
            self.speed = 0
            self.stomp.play()
            self.level.get_save().header.m_uScore += 100

        # Set the time since this Koopa was last hit by the player.
        self.time_since_hit = time.perf_counter()

    # Handle collision detection.
    def collision(self, other, coltype, coldir):
        # Check if the other entity is the player.
        if other.get_class() == "player":
            # If the player has collided with the Koopa recently, do not accept collision.
            if self.time_since_hit + 0.5 > time.perf_counter():
                return False
            
            # Otherwise, if the Koopa is stomped bit not kicked, kick the Koopa.
            elif self.stomped and not self.kicked:
                self.level.get_save().header.m_uScore += 400
                self._engine.console.log(f"[Lost Levels]: enemy \"{self.get_class()}\" was kicked")
                self.kicked = True
                self.speed = 300
                self.negate_speed = self.get_abscentre().x - other.get_abscentre().x < 0
                self.time_since_hit = time.perf_counter()
                self.kick.play()
                return False
        
        # Otherwise, if the Koopa is being kicked and the other entity is an enemy,
        # kill it.
        elif self.kicked and isinstance(other, EnemyBase):
            other.invoke_event("kill")
            if isinstance(other, Koopa) and other.kicked:
                self.invoke_event("kill")
            return False
        
        # Otherwise, handle collision as per usual.
        return True
        
    # Handle final collision.
    def collisionfinal(self, name, returnValue, other, coltype, coldir):
        # Handle hitting elements on the other side.
        if coldir == engine.entity.COLDIR_LEFT or coldir == engine.entity.COLDIR_RIGHT:
            # If this is the player, only hurt them if the Koopa is not stomped or being kicked,
            # and the player hasn't hit the Koopa recently.
            if other.get_class() == "player":
                if (self.kicked or not self.stomped) and self.time_since_hit + 0.5 <= time.perf_counter():
                    other.hurt()
                    return engine.Event.DETOUR_CONTINUE
                
            # Otherwise, if the Koopa is being kicked, play an impact sound.
            else:
                self.block_hit_sound.repeat()
            
        # If the player hit this enemy from above, invoke the player_hit event.
        if engine.entity.is_collision_above(coltype, coldir) and other.get_class() == "player":
            other.add_velocity_y = 400
            other.jump_multiplier = 1.2
            self.invoke_event("player_hit", other)
            return engine.Event.DETOUR_CONTINUE

        # Return?
        return engine.Event.DETOUR_CONTINUE