"""World 1-3."""

import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator

# Define the level data for this level's primary sections.
class Level13_main(levelgenerator.LevelData):
    # Create the level data for the primary sections.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

# Return a path to the image preview of this level.
def get_preview():
    return "engine/assets/missing.png"

# Generate the level data for this level.
def load_leveldata(eng: engine.LLEngine, level: lostlevels.scenes.Level, section):
    # Currently, the only level data used for this level will be Level13_main.
    # As one of the pipes will change the biome used for the main section, the
    # section name must be parsed briefly in order to obtain biome information.

    # Verify that the grammar of the section name is correct.
    split = section.split("_")
    if len(split) > 2:
        return None
    
    # Extract the biome and section information from the section name. Verify the
    # biome given and create the level generator using the biome's name. If there 
    # is no delimiter, assume that the biome is winter.
    if len(split) == 2:
        biome, name = split
    else:
        biome, name = "winter", split[0]
    if biome != "overground" and biome != "winter":
        return None
    gen = levelgenerator.LevelGenerator(eng, level, biome)
    
    # Is this the main section?
    if name == "main":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(52, 0), biome)

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 18, 2)

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # TODO: 8 PIPES, FIRST TYPE TAKES YOU TO "overground_main" AT (52, 0), 
        # THEN ADD INVISIBLE WALL TO THE RIGHT

        # Return the level data generated for this section.
        return data