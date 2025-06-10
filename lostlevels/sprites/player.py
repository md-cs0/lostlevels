"""This is the Lost Levels player sprite, which can be controlled
by the player."""

import time
import pygame
import engine
import lostlevels
from . import Humanoid

# The player class.
class Player(engine.entity.Sprite, Humanoid):
    # Construct a new player.
    def __init__(self, eng, classname):
        # Call the sprite constructor and modify its default properties.
        engine.entity.Sprite.__init__(self, eng, classname)
        Humanoid.__init__(self)
        self.get_event("per_frame").set_func(Player.per_frame)
        self.get_event("collision").set_func(Player.collision)
        self.get_event("collisionfinal").set_func(Player.collisionfinal)
        self.acceleration = 6.5

        # Load the player spritesheet.
        self.load("lostlevels/assets/sprites/player_small.png", (24, 58), 12)

        # Cache the status of the player jumping.
        self.__jumping = 0
        self.__speedwhenjumping = 0

        # Store the timestamp for when the player's animation last changed.
        self.__animtimestamp = 0

        # Cache the status of the player crouching.
        self.__crouching = False

        # Can this player actually move?
        self.moveable = True
        self.can_jump = True
        self.always_animate = False # If Player::moveable is False, should the player still animate itself?

        # Main player status.
        self.can_die = True

        # The level scene object.
        self.level = None
        
        # Instantiate a bunch of sound objects for the player's SFX.
        self.death_sound = self._engine.create_sound("lostlevels/assets/audio/player/death.ogg")
        self.block_hit_sound = self._engine.create_sound("lostlevels/assets/audio/player/block_hit.ogg")
        self.jump_sound = self._engine.create_sound("lostlevels/assets/audio/player/jump.ogg")
        self.denied_sound = self._engine.create_sound("lostlevels/assets/audio/player/denied.ogg")
        self.death_sound.volume = 1
        self.block_hit_sound.volume = 1
        self.jump_sound.volume = 1

        # Used for propelling off enemy targets.
        self.add_velocity_y = 0
        self.jump_multiplier = 1

        # Used for climbing the player.
        self.climbing = False
        self.climb_velocity = 0

    # Handle player movement per-frame.
    def per_frame(self):
        # Override this function if the player is climbing.
        if self.climbing:
            # Correct the movetype so that the player can climb properly.
            self.movetype = engine.entity.MOVETYPE_CUSTOM

            # Force the player's y-velocity to its climb_velocity value and
            # nullify the current x-velocity.
            self.move = 0
            self.velocity = pygame.math.Vector2(0, self.climb_velocity)

            # Fix the player's horizontal origin to the entity being climbed.
            self.set_baseorigin(pygame.math.Vector2(
                self.climbing.get_baseorigin().x - self.get_hitbox().x, self.get_baseorigin().y))

            # Handle the player's climbing animation.
            self.flip() # Make sure the player is facing rightwards.
            if time.perf_counter() > self.__animtimestamp + 0.085:
                if self.index < 8:
                    self.index = 8
                else:
                    self.index -= 8
                    self.index = (self.index + 1) % 4 + 8
                self.__animtimestamp = time.perf_counter()

            # Return.
            return
        else:   
            self.movetype = engine.entity.MOVETYPE_PHYSICS

        # Should this player be animated automatically?
        if self.always_animate or self.moveable:
            # Flip the player sprite in the direction of travel.
            if abs(self.velocity.x) > 0.1:
                self.flip(self.velocity.x < 0)
            
            # Animate the player based on its current movement.
            if self.__crouching:
                self.index = 5
            else:
                if self.groundentity:
                    if abs(self.velocity.x) > 0.1:
                        length = 1 / (abs(self.velocity.x) / 20)
                        if time.perf_counter() > self.__animtimestamp + length:
                            self.__animtimestamp = time.perf_counter()
                            self.index = (self.index % 3) + 1
                    else:
                        self.index = 0
                else:
                    self.index = 4

        # Return if this player can't move.
        if not self.moveable:
            return

        # Accelerate the player in either direction based on which arrow
        # keys are held.
        keys = self._engine.get_keys_dict()
        self.move = 0
        if keys[pygame.K_LEFT]:
            self.move -= 150
        if keys[pygame.K_RIGHT]:
            self.move += 150

        # Accelerate faster if the Z key is held.
        if keys[pygame.K_z]:
            self.move *= 1.75

        # Jump upon pressing X.
        if keys[pygame.K_x] and self.can_jump:
            # Set the timestamp where the player started jumping.
            if (self.groundentity and self.__jumping == -1 
                and not (self.groundentity.game_flags & lostlevels.sprites.CANNOT_JUMP)):
                self.__jumping = time.perf_counter()
                self.__speedwhenjumping = abs(self.velocity.x)
                self.jump_sound.repeat()
            
            # Hold the player upwards depending on whether they are holding the X key
            # and how fast they're moving.
            multiplier = max(min(abs(self.__speedwhenjumping), 150) / 125, 1)
            if self.__jumping + 0.3 > time.perf_counter():
                self.velocity.y = 350 * multiplier * self.jump_multiplier
        else:
            self.__jumping = -1

        # Handle crouching upon pressing the downwards arrow key and set the
        # player's hitbox size.
        if self.groundentity:
            # Reset the jump multiplier.
            if self.add_velocity_y == 0:
                self.jump_multiplier = 1

            # Set the crouching state.
            if keys[pygame.K_DOWN]:
                if not self.__crouching:
                    self.__crouching = True
                    self.set_hitbox(pygame.math.Vector2(24, 30))
                    self.set_baseorigin(self.get_baseorigin() - pygame.math.Vector2(0, 28))
            else:
                if self.__crouching:
                    self.set_hitbox(pygame.math.Vector2(24, 58))
                    self.set_baseorigin(self.get_baseorigin() + pygame.math.Vector2(0, 28))
                self.__crouching = False

            # Nullify any ground movment while crouching.
            if self.__crouching:
                self.move = 0

        # Add the player's add velocity to the actual velocity.
        if self.add_velocity_y != 0:
            self.velocity.y = self.add_velocity_y
            self.add_velocity_y = 0

    # Override the player's collision.
    def collision(self, other, coltype, coldir):
        # If this player is alive, handle collision in all cases.
        if self.alive:
            return True
        
        # Otherwise, do not collide with anything.
        return False

    # Handle additional collision resolution code.
    def collisionfinal(self, other, coltype, coldir):
        # If this player hit another entity from below, stop jumping.
        if (engine.entity.is_collision_above(coltype, coldir)):
            self.__jumping = -1
            self.block_hit_sound.repeat()
        
        # If this player was hit by a falling entity, kill the player.
        if (coltype == engine.entity.COLTYPE_COLLIDED and coldir == engine.entity.COLDIR_UP
            and self.level):
            self.level.death()

        # If the player landed at an insanely fast speed, kill the player.
        if (self.velocity.y < -1250 and coltype == engine.entity.COLTYPE_COLLIDING 
            and coldir == engine.entity.COLDIR_UP and self.level):
            self.level.death()

    # Used for utilizing entities.
    def keydown(self, enum, unicode, focused):
        # If this is the Z key, fire a weapon if equipped and return.
        if enum == pygame.K_z and self.weapon:
            self.weapon.invoke_event("fire")
            return

        # Check that this is the USE key.
        if not enum == pygame.K_e:
            return

        # Generate a list of entities close to the player.
        start = self.get_topleft() + pygame.math.Vector2(-30, 30)
        end = self.get_bottomright() + pygame.math.Vector2(30, -30)
        entities = self._engine.query_entities(start, end)

        # Find the closest entity to the player that can be used.
        closest = None
        closest_dist = 0
        for entity in entities:
            if not entity.can_use:
                continue
            diff = entity.get_centre() - self.get_centre()
            dist = diff.x ** 2 + diff.y ** 2
            if not closest or dist < closest_dist:
                closest = entity

        # Invoke the use event of the selected entity, if found.
        if closest:
            closest.invoke_event("use")
        else:
            self.denied_sound.repeat()

    # Kill this player. This method should not be called.
    def kill(self):
        # Invalidate the player's alive status.
        self.alive = False

        # Change the player to the death pose.
        self.moveable = False
        self.index = 7
        self.velocity = pygame.math.Vector2(0, 500)
        self.move = 0

        # Log the player's death and play the death sound.
        self.death_sound.play()
        self._engine.console.log("[Lost Levels]: the player has died!")

    # Hurt this player. This method should be used instead for downgrading the player or
    # killing the player outright. For always killing the player, see Level::death().
    def hurt(self):
        # For now, this will just kill the player in all circumstances.
        self.level.death()

    # Finish the level by having the player walk to the end while calling the level's
    # Level::finish_level() method.
    def finish_level(self):
        # Have the finish_level() methods already been called?
        if self.level.finished:
            return
        
        # Have the player walk into the distance.
        self.climbing = False
        self.moveable = False
        self.always_animate = True
        self.move = 150 * 1.75

        # Call the level's Level::finish_level() method.
        self.level.finish_level()