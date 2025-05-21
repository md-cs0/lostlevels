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
    # Create the level data for the current section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

        # Manage whether some obstacles have spawned already.
        self.big_goomba_spawned = False

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

        # Create the main ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 15, 2)
        gen.generate_ground(pygame.math.Vector2(896, -416), 10, 2)

        # Create the power-up blocks.
        gen.generate_powerup_block(pygame.math.Vector2(960, -288), spiked = True)
        rocket = gen.generate_powerup_block(pygame.math.Vector2(992, -288), fall = True)
        gen.insert_powerup(rocket[0], "rocket_launcher")

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

        # TEMP
        gen.generate_ground(pygame.math.Vector2(1216, 0), 10, 15)

        return data
    
    # Invalid section?
    return None