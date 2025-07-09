"""World 1-3."""

import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator
from .. import sample_hooks

# Define the level data for this level's primary sections.
class Level13_main(levelgenerator.LevelData):
    # Create the level data for the primary sections.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

# Define the level data for the Goombas section of the level.
class Level13_goombas(levelgenerator.LevelData):
    # Create the level data for the Goombas section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

         # Manage the train.
        self.train_spawned = False
        self.train = None

    # Manage the train.
    def per_frame(self):
        # Once the player reaches the trigger point, spawn a 1996 Stock train
        # that will constantly accelerate, before deleting the train once it
        # reaches far out of the player's view.
        if not self.train_spawned and self._level.player.get_baseorigin().x > 1000:
            # Spawn the 1996 Stock train, as if it came from the previous level.
            self.train = self._engine.create_entity_by_class("sprite")
            self.train.movetype = engine.entity.MOVETYPE_CUSTOM
            self.train.load("lostlevels/assets/sprites/1996_stock.png", (6908, 158), 1)
            self.train.velocity.x = 1200
            self.train.game_flags |= lostlevels.sprites.DO_NOT_DELETE
            self.train.set_baseorigin(pygame.math.Vector2(-7200, -258))
            self.train.get_event("collision").set_func(sample_hooks.boulder_hit)
            self._engine.activate_entity(self.train)
            self.train_spawned = True

            # Play the 1996 Stock sound effect.
            motors = self._engine.create_sound("lostlevels/assets/audio/objects/1996_stock_rolling.ogg")
            motors.volume = 1
            motors.play()

        # If the train has spawned already, accelerate it until it reaches the end of the
        # scene, before it eventually gets deleted.
        if self.train_spawned and self.train:
            # If the train is beyond the player's viewpoint, destroy it.
            if self.train.get_absorigin().x > 576:
                self._engine.delete_entity(self.train)
                self.train = None

# Return a path to the image preview of this level.
def get_preview():
    return "engine/assets/missing.png"

# Generate the level data for this level.
def load_leveldata(eng: engine.LLEngine, level: lostlevels.scenes.Level, section):
    # Currently, the only level data used for this level will be Level13_main.
    # As one of the pipes will change the biome used for the main section, the
    # section name must be parsed briefly in order to obtain biome information.

    # Verify that the grammar of the section name is correct.
    
    # Extract the biome and section information from the section name. Verify the
    # biome given and create the level generator using the biome's name. If there 
    # is no delimiter, assume that the biome is winter.
    split = section.split("_", 1)
    if len(split) == 2:
        biome, name = split
    else:
        biome, name = "winter", split[0]
    gen = levelgenerator.LevelGenerator(eng, level, biome)

    # Is this the main section?
    if name == "main":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(52, 0), biome)

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # Create the ground.
        troll_ground = gen.generate_ground(pygame.math.Vector2(0, -416), 2, 2)
        for ground in troll_ground:
            ground.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: 
                    sample_hooks.unanchor_on_collide(eng, troll_ground, hit, other, coltype, coldir))
        gen.generate_ground(pygame.math.Vector2(64, -416), 16, 2)

        # Create an array of 8 pipes that are all usable.
        for i in range(0, 8):
            gen.generate_pipe_body(pygame.math.Vector2(64 + i * 64, -384))
            if i == 0:
                new_section = "overground_main"
                offset = None
            elif i == 1:
                new_section = "overground_smb2"
                offset = None
            elif i == 5:
                new_section = f"{biome}_goombas"
                offset = None
            gen.generate_pipe_top(pygame.math.Vector2(64 + i * 64, -352), section = new_section, player_offset = offset)

        # Create a wall after the pipes so that the player cannot walk out of the map.
        gen.generate_blocks(pygame.math.Vector2(576, 0), height = 15)

        # Create a funny cloud that will only be reachable by taking a malicious pipe.
        gen.generate_funny_cloud(pygame.math.Vector2(240, -64), spiked = True)

        # Return the level data generated for this section.
        return data
    
    # Is this the "SMB2" section?
    elif name == "smb2" or name == "smb2_spawn_train":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(52, 0), biome)

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # Create the first bit of ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 17, 2)

        # Create a staircase for an invisible block trap.
        gen.generate_blocks(pygame.math.Vector2(160, -384), 4)
        gen.generate_blocks(pygame.math.Vector2(192, -352), 3)
        gen.generate_blocks(pygame.math.Vector2(224, -320), 2)
        gen.generate_blocks(pygame.math.Vector2(256, -288))

        # Create an invisible block to the right of the staircase that will result in
        # the player falling into the trap.
        gen.generate_powerup_block(pygame.math.Vector2(288, -160), draw = False)

        # Create a grid of invisible power-up blocks that will cover the roof of the trap,
        # preventing the player from escaping.
        gen.generate_powerup_block(pygame.math.Vector2(288, -288), 9, draw = False)

        # Create more ground after the trap, with a pipe to the right of the trap.
        # This pipe will lead into some SMB2 jar-like zone.
        gen.generate_ground(pygame.math.Vector2(576, -416), 15, 2)
        gen.generate_pipe_body(pygame.math.Vector2(576, -384), 3)
        gen.generate_pipe_top(pygame.math.Vector2(576, -288), section = "smb2jar_jar")

        # Create a random Koopa.
        gen.generate_koopa(pygame.math.Vector2(832, -368))

        # Add a fake SMB2-like door that leads to a fake underground section.
        smb2 = eng.create_entity_by_class("sprite", eng.entity_head())
        smb2.load("lostlevels/assets/sprites/smb2_door.png", (256, 352), 1)
        smb2.movetype = engine.entity.MOVETYPE_NONE
        smb2.set_baseorigin(pygame.math.Vector2(860, -128))

        # Create some bushes.
        gen.generate_bush(pygame.math.Vector2(704, -384), 4)

        # Create some clouds.
        gen.generate_cloud(pygame.math.Vector2(128, -128))
        gen.generate_cloud(pygame.math.Vector2(416, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(928, -128), 4)

        # Prevent the level from scrolling beyond the door.
        level.max_scroll = 540

        # Create a wall beyond the door as well so that the player cannot progress beyond the map.
        gen.generate_ground(pygame.math.Vector2(1116, 0), height = 15)
        
        # If the player came out of the jar section pipe, spawn a 1996 Stock train.
        if name == "smb2_spawn_train":
            train = eng.create_entity_by_class("sprite")
            train.movetype = engine.entity.MOVETYPE_CUSTOM
            train.load("lostlevels/assets/sprites/1996_stock.png", (6908, 158), 1)
            train.velocity.x = 1200
            train.game_flags |= lostlevels.sprites.DO_NOT_DELETE
            train.set_baseorigin(pygame.math.Vector2(-7600, -258))
            train.get_event("collision").set_func(sample_hooks.boulder_hit)
            eng.activate_entity(train)

            # Play the 1996 Stock sound effect.
            motors = eng.create_sound("lostlevels/assets/audio/objects/1996_stock_rolling.ogg")
            motors.volume = 1
            motors.play()

        # Return the level data generated for this section.
        return data
    
    # Is this the "SMB2" jar section?
    elif name == "jar":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(276, -64), biome)

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Create some invisible blocks for the structure of the map.
        gen.generate_ground(pygame.math.Vector2(0, 32), 18, draw = False)
        gen.generate_ground(pygame.math.Vector2(128, 0), height = 3, draw = False)
        gen.generate_ground(pygame.math.Vector2(416, 0), height = 3, draw = False)
        gen.generate_ground(pygame.math.Vector2(128, -96), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(384, -96), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(64, -128), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(448, -128), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(64, -160), height = 7, draw = False)
        gen.generate_ground(pygame.math.Vector2(480, -160), height = 7, draw = False)
        gen.generate_ground(pygame.math.Vector2(64, -384), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(448, -384), 2, draw = False)
        gen.generate_ground(pygame.math.Vector2(0, -416), 18, draw = False)

        # Create platforms for the player to stand on.
        gen.generate_rope(pygame.math.Vector2(160, -192), 3)
        gen.generate_rope(pygame.math.Vector2(320, -192), 3)
        gen.generate_rope(pygame.math.Vector2(96, -288), 3)
        gen.generate_rope(pygame.math.Vector2(384, -288), 3)

        # Create a pipe for the player to transport back out of.
        body = gen.generate_pipe_body(pygame.math.Vector2(256, 0), lostlevels.sprites.PIPE_180)
        gen.generate_pipe_top(pygame.math.Vector2(256, -32), lostlevels.sprites.PIPE_180,
                              "overground_smb2_spawn_train", pygame.math.Vector2(596, -230))
        
        # Create a key that the player can "use".
        key = eng.create_entity_by_class("sprite", body[0])
        key.load("lostlevels/assets/sprites/smb2_key.png", (28, 32), 1)
        key.set_baseorigin(pygame.math.Vector2(274, -392))
        key.can_use = True

        # SMB2 key: follow the player.
        def key_follow_player():
            key.set_baseorigin(level.player.get_baseorigin() + pygame.math.Vector2(0, 32))
            key.draw = level.player.draw

        # SMB2 key: upon using, set its per_frame event so that the key follows
        # the player.
        def key_use():
            key.movetype = engine.entity.MOVETYPE_NONE
            key.get_event("per_frame").set_func(lambda self: key_follow_player())

        # Set the key's USE function to key_use().
        key.get_event("use").set_func(lambda self: key_use())

        # Return the level data generated for this section.
        return data
    
    # Is this the stack of Goombas section?
    elif name == "goombas":
        # Create the level data for this section.
        data = Level13_goombas(eng, level, pygame.math.Vector2(52, 0), biome)

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 60, 2)

        # Create a power-up block that will emit a funny mushroom.
        powerup_block = gen.generate_powerup_block(pygame.math.Vector2(320, -288))
        gen.insert_powerup(powerup_block[0], "death_cap")

        # Create a stack of Goombas after the power-up block.
        for i in range(0, 16):
            gen.generate_goomba(pygame.math.Vector2(736, -384 + i * 26))

        # Create a levitating platform with some pipe to the next section above the Goombas.
        gen.generate_ground(pygame.math.Vector2(800, -32), 2)
        gen.generate_pipe_body(pygame.math.Vector2(800, 0))
        gen.generate_pipe_top(pygame.math.Vector2(800, 32), section = f"{biome}_end")

        # Create some bushes.
        gen.generate_bush(pygame.math.Vector2(160, -384), 4)
        gen.generate_hill(pygame.math.Vector2(320, -384))
        gen.generate_bush(pygame.math.Vector2(480, -384), 5)
        gen.generate_bush(pygame.math.Vector2(736, -384), 3)
        gen.generate_hill(pygame.math.Vector2(960, -384))
        gen.generate_bush(pygame.math.Vector2(1152, -384), 3)
        gen.generate_bush(pygame.math.Vector2(1472, -384), 4)
        
        # Create some clouds.
        gen.generate_cloud(pygame.math.Vector2(128, -128))
        gen.generate_cloud(pygame.math.Vector2(416, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(928, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(1184, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(1504, -128))

        # Return the level data generated for this section.
        return data
    
    # Is this the end-of-level selection?
    elif name == "end":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(52, 0), biome)

        # Create a pipe that will take the player into the troll cloud in the first section.
        gen.generate_pipe_body(pygame.math.Vector2(288, -384))
        gen.generate_pipe_top(pygame.math.Vector2(288, -352), section = f"{biome}_main", 
                              player_offset = pygame.math.Vector2(272, 32))
        
        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 15, 2)
        
        # Create a platform that will fall down before the player even reaches it.
        falling_platform = gen.generate_platform(pygame.math.Vector2(512, -416), 4)
        def platform_fall():
            if (level.player.get_baseorigin().x > 480 
                and falling_platform[0].movetype == engine.entity.MOVETYPE_CUSTOM):
                for ent in falling_platform:
                    ent.movetype = engine.entity.MOVETYPE_PHYSICS
        for ent in falling_platform:
            ent.get_event("per_frame").set_func(lambda self: platform_fall())

        # Create another platform that will levitate upwards when the player stands on it.
        rising_platform = gen.generate_platform(pygame.math.Vector2(672, -416), 4)
        for ent in rising_platform:
            ent.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: sample_hooks.rise_on_collide(rising_platform))
        
        # Create the final piece of ground with the flagpole.
        gen.generate_ground(pygame.math.Vector2(832, -416), 100, 2)
        gen.generate_blocks(pygame.math.Vector2(832, -384))
        gen.generate_flagpole(pygame.math.Vector2(842, -106))

        # Create some clouds.
        gen.generate_cloud(pygame.math.Vector2(288, -128))
        gen.generate_cloud(pygame.math.Vector2(608, -96))
        gen.generate_cloud(pygame.math.Vector2(896, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(1184, -96), 3)

        # Disable scrolling beyond the flagpole.
        level.max_scroll = 560

        # Create a wall beyond the flagpole as well so that the player cannot progress beyond the map.
        gen.generate_ground(pygame.math.Vector2(1168, 0), height = 15)

        # Return the level data generated for this section.
        return data
    
    # Invalid section?
    return None