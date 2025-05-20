"""World 1-1."""

import sys
import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator

# Define the level data for this level's main section.
class Level11_main(levelgenerator.LevelData):
    # Create the level data for the current section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome)

        # Create the super secret zone text.
        self.secret = eng.create_ui_element_by_class("text")
        self.secret.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.secret.set_size(engine.ui.UDim2(1, 0, 0, 24))
        self.secret.set_position(engine.ui.UDim2(0, 0, 0, 150))
        self.secret.set_text("YOU REACHED THE SUPER SECRET ZONE,\nPLEASE WALK FURTHER AND JUMP INTO THE PIT.")
        self.secret.set_colour(pygame.Color(255, 255, 255))
        self.secret.set_x_align(engine.ui.X_CENTRE)
        self.idiot_played = False

    # Manage the super secret zone.
    def per_frame(self):
        # Handle the "super secret zone".
        if self._level.player.get_baseorigin().x > 6700 and not self._level.finished:
            # Enable the dialogue.
            self.secret.enabled = True
            
            # If the player jumped into the pit, play the you are an idiot sound,
            # before dying, and freeze the game so that the audio can play.
            if self._level.player.get_baseorigin().y < -600 and not self.idiot_played:
                self._level.stop_music()
                idiot = self._engine.create_sound("lostlevels/assets/audio/you_are_an_idiot.ogg")
                idiot.play()
                while idiot.playing():
                    pass
                self.idiot_played = True

# Return a path to the image preview of this level.
def get_preview():
    return "engine/assets/missing.png"

# Generate the level data for this level.
def load_leveldata(eng: engine.LLEngine, level: lostlevels.scenes.Level, section):
    # Is this the main section?
    if section == "main":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(eng, level, "overground")
        data = Level11_main(eng, level, pygame.math.Vector2(32, -358), "overground")

        # Create the main ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 69, 2)
        gen.generate_ground(pygame.math.Vector2(2272, -416), 15, 2)
        gen.generate_ground(pygame.math.Vector2(2848, -416), 64, 2)
        gen.generate_ground(pygame.math.Vector2(4960, -416), 80, 2)

        # Create the power-up blocks.
        gen.generate_powerup_block(pygame.math.Vector2(512, -288))
        gen.generate_powerup_block(pygame.math.Vector2(672, -288), fall = True)
        gen.generate_powerup_block(pygame.math.Vector2(672, -320), draw = False)
        gen.generate_powerup_block(pygame.math.Vector2(736, -288))
        gen.generate_powerup_block(pygame.math.Vector2(704, -160))
        hidden = gen.generate_powerup_block(pygame.math.Vector2(2048, -256), draw = False)
        gen.insert_powerup(hidden[0], "glitch_powerup")
        gen.generate_powerup_block(pygame.math.Vector2(2496, -288))
        gen.generate_powerup_block(pygame.math.Vector2(3008, -160))
        gen.generate_powerup_block(pygame.math.Vector2(3008, -288), decoy = True)
        gen.generate_powerup_block(pygame.math.Vector2(3232, -288), decoy = True)
        gen.generate_powerup_block(pygame.math.Vector2(3392, -288))
        gen.generate_powerup_block(pygame.math.Vector2(3488, -288))
        gen.generate_powerup_block(pygame.math.Vector2(3584, -288))
        gen.generate_powerup_block(pygame.math.Vector2(3488, -160))
        gen.generate_powerup_block(pygame.math.Vector2(4128, -160), 2)
        gen.generate_powerup_block(pygame.math.Vector2(5440, -288))

        # Create the destructible blocks.
        gen.generate_destructible(pygame.math.Vector2(640, -288))
        gen.generate_destructible(pygame.math.Vector2(704, -288))
        gen.generate_destructible(pygame.math.Vector2(768, -288))
        gen.generate_destructible(pygame.math.Vector2(2464, -288))
        gen.generate_destructible(pygame.math.Vector2(2528, -288))
        gen.generate_destructible(pygame.math.Vector2(2560, -160), 8)
        gen.generate_destructible(pygame.math.Vector2(2912, -160), 3)
        gen.generate_destructible(pygame.math.Vector2(3200, -288))
        gen.generate_destructible(pygame.math.Vector2(3776, -288))
        gen.generate_destructible(pygame.math.Vector2(3872, -160), 3)
        gen.generate_destructible(pygame.math.Vector2(4096, -160))
        gen.generate_destructible(pygame.math.Vector2(4192, -160))
        gen.generate_destructible(pygame.math.Vector2(4128, -288), 2)
        gen.generate_destructible(pygame.math.Vector2(5376, -288), 2)
        gen.generate_destructible(pygame.math.Vector2(5472, -288))

        # Create the pipes.
        gen.generate_pipe_body(pygame.math.Vector2(896, -384))
        gen.generate_pipe_top(pygame.math.Vector2(896, -352))
        gen.generate_pipe_body(pygame.math.Vector2(1216, -384), 2)
        gen.generate_pipe_top(pygame.math.Vector2(1216, -320))
        gen.generate_pipe_body(pygame.math.Vector2(1472, -384), 3)
        gen.generate_pipe_top(pygame.math.Vector2(1472, -288))
        gen.generate_pipe_body(pygame.math.Vector2(1824, -384), 3)
        gen.generate_pipe_top(pygame.math.Vector2(1824, -288), section = "bonus")
        gen.generate_pipe_body(pygame.math.Vector2(5216, -384))
        gen.generate_pipe_top(pygame.math.Vector2(5216, -352))
        gen.generate_pipe_body(pygame.math.Vector2(5728, -384))
        gen.generate_pipe_top(pygame.math.Vector2(5728, -352))

        # Create the blocks.
        gen.generate_blocks(pygame.math.Vector2(4288, -384), 4)
        gen.generate_blocks(pygame.math.Vector2(4320, -352), 3)
        gen.generate_blocks(pygame.math.Vector2(4352, -320), 2)
        gen.generate_blocks(pygame.math.Vector2(4384, -288))
        gen.generate_blocks(pygame.math.Vector2(4480, -288))
        gen.generate_blocks(pygame.math.Vector2(4480, -320), 2)
        gen.generate_blocks(pygame.math.Vector2(4480, -352), 3)
        gen.generate_blocks(pygame.math.Vector2(4480, -384), 4)
        gen.generate_blocks(pygame.math.Vector2(4736, -384), 5)
        gen.generate_blocks(pygame.math.Vector2(4768, -352), 4)
        gen.generate_blocks(pygame.math.Vector2(4800, -320), 3)
        gen.generate_blocks(pygame.math.Vector2(4832, -288), 2)
        gen.generate_blocks(pygame.math.Vector2(4960, -288))
        gen.generate_blocks(pygame.math.Vector2(4960, -320), 2)
        gen.generate_blocks(pygame.math.Vector2(4960, -352), 3)
        gen.generate_blocks(pygame.math.Vector2(4960, -384), 4)
        gen.generate_blocks(pygame.math.Vector2(5792, -384), 9)
        gen.generate_blocks(pygame.math.Vector2(5824, -352), 8)
        gen.generate_blocks(pygame.math.Vector2(5856, -320), 7)
        gen.generate_blocks(pygame.math.Vector2(5888, -288), 6)
        gen.generate_blocks(pygame.math.Vector2(5920, -256), 5)
        gen.generate_blocks(pygame.math.Vector2(5952, -224), 4)
        gen.generate_blocks(pygame.math.Vector2(5984, -192), 3)
        gen.generate_blocks(pygame.math.Vector2(6016, -160), 2)
        gen.generate_blocks(pygame.math.Vector2(6048, -128))
        gen.generate_blocks(pygame.math.Vector2(6336, -384))

        # Create the hills.
        gen.generate_hill(pygame.math.Vector2(0, -384))
        gen.generate_hill(pygame.math.Vector2(512, -384))
        gen.generate_hill(pygame.math.Vector2(1536, -384))
        gen.generate_hill(pygame.math.Vector2(2048, -384))
        gen.generate_hill(pygame.math.Vector2(3136, -384))
        gen.generate_hill(pygame.math.Vector2(3552, -384))
        gen.generate_hill(pygame.math.Vector2(4672, -384))
        gen.generate_hill(pygame.math.Vector2(5152, -384))
        gen.generate_hill(pygame.math.Vector2(6176, -384))

        # Create the bushes.
        gen.generate_bush(pygame.math.Vector2(384, -384), 4)
        gen.generate_bush(pygame.math.Vector2(736, -384))
        gen.generate_bush(pygame.math.Vector2(1312, -384), 3)
        gen.generate_bush(pygame.math.Vector2(1920, -384), 4)
        gen.generate_bush(pygame.math.Vector2(2304, -384))
        gen.generate_bush(pygame.math.Vector2(2880, -384), 3)
        gen.generate_bush(pygame.math.Vector2(3424, -384), 4)
        gen.generate_bush(pygame.math.Vector2(3840, -384))
        gen.generate_bush(pygame.math.Vector2(4416, -384))
        gen.generate_bush(pygame.math.Vector2(5376, -384))

        # Create the clouds.
        gen.generate_cloud(pygame.math.Vector2(288, -128))
        gen.generate_cloud(pygame.math.Vector2(608, -96))
        gen.generate_cloud(pygame.math.Vector2(896, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(1184, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(1792, -128))
        gen.generate_cloud(pygame.math.Vector2(2176, -96))
        gen.generate_cloud(pygame.math.Vector2(2400, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(2720, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(3328, -128))
        gen.generate_cloud(pygame.math.Vector2(3680, -96))
        gen.generate_cloud(pygame.math.Vector2(3968, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(4256, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(4896, -128))
        gen.generate_cloud(pygame.math.Vector2(5248, -96))
        gen.generate_cloud(pygame.math.Vector2(5504, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(5792, -96), 3)
        gen.generate_cloud(pygame.math.Vector2(6432, -128))

        # Create the Goombas.
        gen.generate_goomba(pygame.math.Vector2(704, -390))
        gen.generate_goomba(pygame.math.Vector2(1280, -390))
        gen.generate_goomba(pygame.math.Vector2(1632, -390))
        gen.generate_goomba(pygame.math.Vector2(1680, -390))
        gen.generate_goomba(pygame.math.Vector2(2560, -134))
        gen.generate_goomba(pygame.math.Vector2(2624, -134))
        gen.generate_goomba(pygame.math.Vector2(3104, -390))
        gen.generate_goomba(pygame.math.Vector2(3152, -390))
        gen.generate_goomba(pygame.math.Vector2(3648, -390))
        gen.generate_goomba(pygame.math.Vector2(3696, -390))
        gen.generate_goomba(pygame.math.Vector2(3968, -390))
        gen.generate_goomba(pygame.math.Vector2(4016, -390))
        gen.generate_goomba(pygame.math.Vector2(4096, -390))
        gen.generate_goomba(pygame.math.Vector2(4144, -390))
        gen.generate_goomba(pygame.math.Vector2(5568, -390))
        gen.generate_goomba(pygame.math.Vector2(5616, -390))

        # Create the Koopa.
        gen.generate_koopa(pygame.math.Vector2(3424, -368))

        # Create the flagpole.
        gen.generate_flagpole(pygame.math.Vector2(6346, -106))

        # Return the level data generated for this section.
        return data
    
    # Is this the "bonus" section?
    elif section == "bonus":
        # Create the level generator and level data for this section.
        gen = levelgenerator.LevelGenerator(eng, level, "underground")
        data = Level11_main(eng, level, pygame.math.Vector2(48, -64), "underground")

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 18, 2)

        # Create a wall, roof and a stage consisting of destructible blocks.
        gen.generate_destructible(pygame.math.Vector2(0, -64), height = 11)
        gen.generate_destructible(pygame.math.Vector2(128, -64), 9)
        gen.generate_destructible(pygame.math.Vector2(128, -320), 9, 3)

        # Create the exit pipe.
        gen.generate_pipe_2x2(pygame.math.Vector2(544, -384), leftroot = True)
        gen.generate_pipe_body(pygame.math.Vector2(544, -320), 9)
        gen.generate_pipe_body(pygame.math.Vector2(512, -352), orientation = lostlevels.sprites.PIPE_270)
        gen.generate_pipe_top(pygame.math.Vector2(480, -352), lostlevels.sprites.PIPE_270, "main",
                              pygame.math.Vector2(5236, -294))
        
        # Generate a computer that will crash the game upon using it.
        computer = eng.create_entity_by_class("sprite")
        computer.load("lostlevels/assets/sprites/monitor.png", (67, 59), 1)
        computer.set_baseorigin(pygame.math.Vector2(239, -261))
        computer.can_use = True
        computer.get_event("use").set_func(panic)

        # Generate signs for the computer as well.
        signs = eng.create_entity_by_class("sprite")
        signs.movetype = engine.entity.MOVETYPE_NONE
        signs.load("lostlevels/assets/sprites/bsod_computer_signs.png", (576, 480), 1)

        # Return the level data generated for this section.
        return data
    
    # Invalid section?
    return None
    
# Internal function for the crashing computer.
def panic(self):
    # Play the crash chime depicted in some Power Macintosh computers, such as the
    # Power Macintosh 8100, and wait until the sound has finished playing.
    crash = self._engine.create_sound("lostlevels/assets/audio/objects/car_crash.ogg")
    crash.volume = 1
    crash.play()
    while crash.playing():
        pass

    # Exit abruptly.
    sys.exit(1)