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

        # Return the level data for the main section.
        return data
    
    # Invalid section?
    return None