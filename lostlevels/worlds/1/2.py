"""World 1-1."""

import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator

# Define the level data for this level's main section.
class Level11_main(levelgenerator.LevelData):
    # Create the level data for the current section.
    def __init__(self, engine, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(engine, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

# Return a path to the image preview of this level.
def get_preview():
    return "engine/assets/missing.png"

# Generate the level data for this level.
def load_leveldata(engine: engine.LLEngine, level: lostlevels.scenes.Level, section):
    # Is this the main section?
    if section == "main":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(engine, level, "overground")
        data = Level11_main(engine, level, pygame.math.Vector2(0, 0), "overground")

        # Temp.
        gen.generate_ground(pygame.math.Vector2(0, -416), 50, 2)
        gen.generate_destructible(pygame.math.Vector2(128, -288), 4)
        gen.generate_hill(pygame.math.Vector2(128, -384))
        gen.generate_bush(pygame.math.Vector2(256, -384), 10)
        gen.generate_cloud(pygame.math.Vector2(512, -64), 4)
        gen.generate_funny_cloud(pygame.math.Vector2(768, -64))
        gen.generate_blocks(pygame.math.Vector2(768, -384), 10)
        gen.generate_void(pygame.math.Vector2(992, -288), 3, 3)
        gen.generate_blocks(pygame.math.Vector2(1056, -288), 1, 3)
        gen.generate_athletic(pygame.math.Vector2(1728, -288), 5)
        gen.generate_rope(pygame.math.Vector2(1760, -192), 5)
        gen.generate_platform(pygame.math.Vector2(2144, -128), 4)
        gen.generate_ballpoint(pygame.math.Vector2(2656, -448))
        gen.generate_ice(pygame.math.Vector2(2688, -416), 50, 2)

        # Temp.
        gen.generate_powerup_block(pygame.math.Vector2(320, -288), 2)
        gen.generate_powerup_block(pygame.math.Vector2(384, -288), decoy = True)
        gen.generate_powerup_block(pygame.math.Vector2(416, -288), fall = True)
        gen.generate_coin(pygame.math.Vector2(320, -224), 4)

        # Temp.
        gen.generate_pipe_body(pygame.math.Vector2(1152, -384), 2, lostlevels.sprites.PIPE_0)
        gen.generate_pipe_2x2(pygame.math.Vector2(1152, -320), lostlevels.sprites.PIPE_0, True, True)
        gen.generate_pipe_top(pygame.math.Vector2(1152, -256), lostlevels.sprites.PIPE_0)
        gen.generate_pipe_body(pygame.math.Vector2(1120, -96), 5, lostlevels.sprites.PIPE_90)
        gen.generate_pipe_2x2(pygame.math.Vector2(1280, -96), lostlevels.sprites.PIPE_90, True, True)
        gen.generate_pipe_top(pygame.math.Vector2(1344, -96), lostlevels.sprites.PIPE_90)
        gen.generate_pipe_body(pygame.math.Vector2(1280, -160), 5, lostlevels.sprites.PIPE_270)
        gen.generate_pipe_2x2(pygame.math.Vector2(1120, -160), lostlevels.sprites.PIPE_270, True, True)
        gen.generate_pipe_top(pygame.math.Vector2(1056, -160), lostlevels.sprites.PIPE_270)
        gen.generate_pipe_body(pygame.math.Vector2(1216, -320), 2, lostlevels.sprites.PIPE_180)
        gen.generate_pipe_2x2(pygame.math.Vector2(1216, -256), lostlevels.sprites.PIPE_180, True, True)
        gen.generate_pipe_top(pygame.math.Vector2(1216, -384), lostlevels.sprites.PIPE_180)

        # Temp.
        gen.generate_pipe_body(pygame.math.Vector2(1536, -384), 4)
        gen.generate_pipe_top(pygame.math.Vector2(1536, -256), section = "other")

        # Temp.
        gen.generate_powerup_block(pygame.math.Vector2(64, -288), draw = False)
        gen.generate_destructible(pygame.math.Vector2(96, -288), draw = False)

        # Temp.
        gen.generate_powerup_block(pygame.math.Vector2(320, -160), spiked = True)

        # Return the level data generated for this section.
        return data
    
    # Is this the "other" section?
    elif section == "other":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(engine, level, "underground")
        data = Level11_main(engine, level, pygame.math.Vector2(0, 0), "underground")

        # Temp.
        gen.generate_ground(pygame.math.Vector2(0, -416), 50, 2)
        
        # Return the level data generated for this section.
        return data