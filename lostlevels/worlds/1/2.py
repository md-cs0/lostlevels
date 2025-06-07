"""World 1-2."""

import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator
from .. import sample_hooks

# Define the level data for this level's main section.
class Level12_main(levelgenerator.LevelData):
    # Create the level data for the main section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

        # Manage whether some obstacles have spawned already.
        self.big_goomba_spawned = False
        self.boulder_spawned = False

        # Manage the falling pipe top.
        self.falling_pipe_top = None

        # Set the time limit to 150.
        self.time_limit = 150

    # Manage certain obstacles.
    def per_frame(self):
        # Create a Goomba that should fall from the sky when the player moves 
        # slightly from the spawn point.
        if (not self.big_goomba_spawned and self._level.player.get_baseorigin().x > 160
            and self._level.player.get_baseorigin().x < 736):
            # Spawn the Goomba itself.
            goomba = self._engine.create_entity_by_class("sprite")
            goomba.load("lostlevels/assets/sprites/big_goomba.png", (160, 130), 1)
            goomba.set_baseorigin(pygame.math.Vector2(224, 130))
            goomba.velocity.y = -500
            self._engine.activate_entity(goomba)
            self.big_goomba_spawned = True

            # Play a screaming sound effect.
            screaming = self._engine.create_sound("lostlevels/assets/audio/objects/scream.ogg")
            screaming.volume = 1
            screaming.play()

        # Create a timer for creating a boulder when the player is within the destructible wall.
        if (not self.boulder_spawned and self._level.player.get_baseorigin().x > 3072
            and self._level.player.get_baseorigin().x < 3648):
            # Play the boulder sound effect.
            boulder = self._engine.create_sound("lostlevels/assets/audio/objects/boulder.ogg")
            boulder.volume = 1
            boulder.play()

            # Create a timer for creating a boulder after 0.5s.
            self._engine.create_timer(self.create_boulder, 0.5)
            self.boulder_spawned = True

        # Once the player reaches the end of the level, unanchor the vertical pipe top.
        if self._level.player.get_baseorigin().x > 4288:
            for top in self.falling_pipe_top:
                top.movetype = engine.entity.MOVETYPE_PHYSICS

    # Create the boulder.
    def create_boulder(self):
        boulder = self._engine.create_entity_by_class("rect")
        boulder.movetype = engine.entity.MOVETYPE_CUSTOM
        boulder.colour = pygame.Color(128, 128, 128)
        boulder.set_hitbox(pygame.math.Vector2(48, 48))
        boulder.set_baseorigin(pygame.math.Vector2(self._level.player.get_baseorigin().x - 288, -368))
        boulder.velocity.x = 1152
        boulder.get_event("collision").set_func(boulder_hit)

# Define the level data for this level's underground section.
class Level12_underground(levelgenerator.LevelData):
    # Create the level data for the underground section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

        # Cache the non-collideable wall, as the train entity must be linked before its
        # first entity
        self.wall = None

        # Manage the train.
        self.train_spawned = False
        self.train = None

    # Manage certain obstacles.
    def per_frame(self):
        # Once the player reaches the trigger point, spawn a 1996 Stock train
        # that will constantly accelerate, before deleting the train once it
        # reaches far out of the player's view.
        if (not self.train_spawned and self._level.player.get_baseorigin().x > 1152
            and self._level.player.get_baseorigin().x < 1312):
            # Spawn the 1996 Stock train.
            self.train = self._engine.create_entity_by_class("sprite", self.wall[0])
            self.train.movetype = engine.entity.MOVETYPE_CUSTOM
            self.train.load("lostlevels/assets/sprites/1996_stock.png", (6908, 158), 1)
            self.train.set_baseorigin(pygame.math.Vector2(-6044, -290))
            self.train.get_event("collision").set_func(boulder_hit)
            self._engine.activate_entity(self.train)
            self.train_spawned = True

            # Play the 1996 Stock sound effect.
            motors = self._engine.create_sound("lostlevels/assets/audio/objects/1996_stock.ogg")
            motors.volume = 1
            motors.play()

        # If the train has spawned already, accelerate it until it reaches the end of the
        # scene, before it eventually gets deleted.
        if self.train_spawned and self.train:
            # Accelerate the train gradually.
            self.train.velocity.x += 80 * self._engine.globals.frametime

            # If the train is beyond the player's viewpoint, destroy it.
            if self.train.get_absorigin().x > 576:
                self._engine.delete_entity(self.train)
                self.train = None

# If the boulder hits something within the player's viewpoint, destroy it.
def boulder_hit(self, other, coltype, coldir):
    # If this is not caused by the boulder itself, continue.
    if coltype != engine.entity.COLTYPE_COLLIDING:
        return
    
    # If the other entity is not within the player's viewpoint, continue.
    if other.get_absorigin().x > 576:
        return
    
    # Destroy the entity.
    self._engine.delete_entity(other)

# Return a path to the image preview of this level.
def get_preview():
    return "engine/assets/missing.png"

# Generate the level data for this level.
def load_leveldata(eng: engine.LLEngine, level: lostlevels.scenes.Level, section):
    # Is this the main section?
    if section == "main":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(eng, level, "desert")
        data = Level12_main(eng, level, pygame.math.Vector2(32, -358), "desert")

        # Rocket power-up block: upon releasing the rocket launcher, a Goomba
        # should immediately fall from the sky.
        def rocket_block_goomba(self, name, returnValue):
            gen.generate_goomba(pygame.math.Vector2(960, 100), negate_speed = False, spiked = True)
            return engine.Event.DETOUR_CONTINUE

        # Create the intial ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 15, 2)
        gen.generate_ground(pygame.math.Vector2(896, -416), 200, 2)

        # Just after the initial platform, there should be a layer of ground
        # that immediately falls down the moment the player walks onto it.
        troll_ground = gen.generate_ground(pygame.math.Vector2(480, -416), 13, 2)
        for ground in troll_ground:
            ground.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_on_collide(eng, troll_ground, hit, other, coltype, coldir))
            
        # Create two hidden power-up block just before the troll platform for the player to jump off.
        gen.generate_powerup_block(pygame.math.Vector2(448, -256), draw = False)
        gen.generate_powerup_block(pygame.math.Vector2(480, -96), draw = False)

        # Create the power-up blocks for some rocket launcher area.
        gen.generate_powerup_block(pygame.math.Vector2(960, -288), spiked = True)
        rocket = gen.generate_powerup_block(pygame.math.Vector2(992, -288), fall = True)
        rocket[0].get_event("release_fixed").hook(rocket_block_goomba)
        gen.insert_powerup(rocket[0], "rocket_launcher")

        # After the rocket launcher area, there should be a small hovering shelter
        # alongside a stack of Goombas.
        shelter = gen.generate_blocks(pygame.math.Vector2(1664, -288), 3)
        shelter.extend(gen.generate_blocks(pygame.math.Vector2(1728, -320), height = 2))
        for block in shelter:
            block.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_player_only(eng, shelter, hit, other, coltype, coldir))
        for i in range(0, 16):
            gen.generate_goomba(pygame.math.Vector2(2048, -384 + i * 26))

        # Create a "bush" after the stack of Goombas that will instead render as
        # "missing textures", i.e. the placeholder entries used in the desert biome's
        # tilesheets. Yes, this is intentional.
        gen.generate_bush(pygame.math.Vector2(2272, -384), 4)

        # Create a wall after the bush which is too tall to jump over, but contains
        # invisible blocks next to it, allowing the player to propel themselves
        # upwards. One of the invisible power-up blocks will be spiked.
        gen.generate_blocks(pygame.math.Vector2(2496, -96), height = 10)
        gen.generate_powerup_block(pygame.math.Vector2(2464, -256), draw = False)
        gen.generate_powerup_block(pygame.math.Vector2(2432, -256), draw = False, spiked = True)

        # Create a stack of destructible blocks with a Koopa.
        gen.generate_destructible(pygame.math.Vector2(2944, -96), 8, 10)
        gen.generate_koopa(pygame.math.Vector2(2752, -368))

        # Create the wall that must be destroyed by the rocket launcher. A Goomba
        # is created to help the player with destroying the wall.
        gen.generate_blocks(pygame.math.Vector2(3744, -96), height = 10)
        gen.generate_goomba(pygame.math.Vector2(3712, -390))

        # Create a checkpoint after the wall. It should be far enough away so that it
        # cannot get blown up by the rocket launcher.
        gen.generate_checkpoint(pygame.math.Vector2(4096, -337))

        # Sideways pipe at the end of the overground section: launch a boulder outwards
        # and kill the player.
        def side_pipe_collisionfinal(self, other, coltype, coldir):
            # If the other entity is not the player, continue.
            if other.get_class() != "player":
                return

            # If the player is already dead, continue.
            if not other.alive:
                return
            
            # Play the boulder sound effect.
            boulder = self._engine.create_sound("lostlevels/assets/audio/objects/boulder.ogg")
            boulder.volume = 1
            boulder.play()
            
            # Create a boulder and kill the player.
            boulder = self._engine.create_entity_by_class("rect", self)
            boulder.movetype = engine.entity.MOVETYPE_PHYSICS
            boulder.colour = pygame.Color(128, 128, 128)
            boulder.set_hitbox(pygame.math.Vector2(48, 48))
            boulder.set_baseorigin(pygame.math.Vector2(4464, -368))
            boulder.velocity = pygame.math.Vector2(-1152, 200)
            self.level.death()
            self.movetype = engine.entity.MOVETYPE_NONE

        # Create the final part of this level where two pipes exist. One pipe will
        # launch a boulder at the player, whereas the other will fall from the sky but
        # actually allow the player to enter the underground section.
        gen.generate_pipe_2x2(pygame.math.Vector2(4544, -384), leftroot = True)
        gen.generate_pipe_body(pygame.math.Vector2(4512, -352), orientation = lostlevels.sprites.PIPE_270)
        gen.generate_pipe_body(pygame.math.Vector2(4544, -320))
        data.falling_pipe_top = gen.generate_pipe_top(pygame.math.Vector2(4544, 100), 
                                                      section = "underground")
        for top in data.falling_pipe_top:
            top.movetype = engine.entity.MOVETYPE_ANCHORED
        side = gen.generate_pipe_top(pygame.math.Vector2(4480, -352), lostlevels.sprites.PIPE_270)
        side[0].get_event("collisionfinal").set_func(side_pipe_collisionfinal)

        # Disable scrolling beyond these pipes.
        level.max_scroll = 4032

        # Create a wall beyond the pipes as well so that the player cannot progress beyond the map.
        gen.generate_ground(pygame.math.Vector2(4608, 0), height = 15)

        # Return the level data for the main section.
        return data
    
    # Is this the underground section?
    elif section == "underground":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(eng, level, "underground")
        data = Level12_underground(eng, level, pygame.math.Vector2(64, -64), "underground")

        # Create the left wall and ceiling.
        gen.generate_destructible(pygame.math.Vector2(0, -64), height = 11)
        gen.generate_destructible(pygame.math.Vector2(128, -64), 61)

        # Create the initial ground. The part that the player will land on will
        # unanchor itself once the player collides with it.
        gen.generate_ground(pygame.math.Vector2(0, -416), 2, 2)
        troll_ground = gen.generate_ground(pygame.math.Vector2(64, -416), 1, 2)
        for ground in troll_ground:
            ground.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_on_collide(eng, troll_ground, hit, other, coltype, coldir))
        gen.generate_ground(pygame.math.Vector2(96, -416), 7, 2)

        # Create some elevated ground.
        gen.generate_ground(pygame.math.Vector2(288, -288), height = 4)
        gen.generate_ground(pygame.math.Vector2(288, -256), 25)

        # Prior to a scene that will feature a train, insert two power-up blocks. The player
        # can use this to propel themselves upwards and onto the roof, where there will
        # also be a bunch of Goombas.
        gen.generate_powerup_block(pygame.math.Vector2(640, -160), 2)
        for i in range(0, 16):
            gen.generate_goomba(pygame.math.Vector2(1216, -32 + i * 26))

        # Create the platform and walls for the train that will come out later.
        gen.generate_ground(pygame.math.Vector2(320, -448), 55)
        data.wall = gen.generate_ground(pygame.math.Vector2(320, -288), length = 19, height = 5)
        for block in data.wall:
            block.movetype = engine.entity.MOVETYPE_NONE
        gen.generate_void(pygame.math.Vector2(928, -288), length = 5, height = 5)

        # Create a falling platform after the elevated ground.
        falling_platform = gen.generate_ground(pygame.math.Vector2(1088, -256), length = 4)
        for ground in falling_platform:
            ground.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_on_collide(eng, falling_platform, hit, other, coltype, coldir))
            
        # Create some additional ground and another wall. Some of the wall will be destroyed
        # by the train, allowing the player to progress through the map if the train is
        # utilised correctly.
        gen.generate_ground(pygame.math.Vector2(1216, -256), 2)
        gen.generate_ground(pygame.math.Vector2(1280, -96), height = 11)
        gen.generate_ground(pygame.math.Vector2(1312, -256))
        gen.generate_ground(pygame.math.Vector2(1440, -256), 20)

        # Create another falling platform on the other side.
        falling_platform_for_use = gen.generate_ground(pygame.math.Vector2(1344, -256), length = 3)
        for ground in falling_platform_for_use:
            ground.velocity.y = 200
            ground.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_on_collide(eng, falling_platform_for_use, hit, other, coltype, 
                                                     coldir, True))
            
        # At the end of the lower half of the map, block it off with a wall and a pipe that
        # will just simply take you back to the start of the underground map.
        gen.generate_ground(pygame.math.Vector2(2048, -288), height = 5)
        gen.generate_pipe_body(pygame.math.Vector2(1984, -416))
        gen.generate_pipe_top(pygame.math.Vector2(1984, -384), section = "underground",
                              player_offset = pygame.math.Vector2(64, -64))
        
        # Rising platform: increase the velocity per gravity per frame.
        def platform_per_frame(self):
            self.velocity.y += self._engine.find_gvar("gravity").get() * self._engine.globals.frametime
        
        # Rising platform: upon collision, configure the per_frame event.
        def platform_collisionfinal(group):
            for piece in group:
                piece.get_event("per_frame").set_func(platform_per_frame)

        # Create a platform that rises, instead of falls, upon standing on.
        rising_platform = gen.generate_platform(pygame.math.Vector2(2208, -288), 4)
        for piece in rising_platform:
            piece.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: platform_collisionfinal(rising_platform))
            
        # Create the flagpole area.
        gen.generate_ground(pygame.math.Vector2(2528, -416), 100, 2)
        gen.generate_blocks(pygame.math.Vector2(2848, -384))
        gen.generate_flagpole(pygame.math.Vector2(2858, -106))

        # Return the level data for the underground section.
        return data
    
    # Invalid section?
    return None