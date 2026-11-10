"""World 1-3."""

import random
import time
import pygame
import engine
import lostlevels
import lostlevels.scenes
import lostlevels.sprites

from .. import levelgenerator
from .. import sample_hooks
from ... import effects

# Manage whether the frames for Coldplay's Higher Power have been preloaded.
preloaded_coldplay_higher_power = False
coldplay_higher_power_frame_count = 122

# Suffix to add to the end of the biome name when playing a biome's given music.
biome_music_suffix = ""

# Store whether the player currently holds a key.
holding_key = False

# Due the way the module is named, the world 1-1 module must be loaded dynamically.
world_1_1_module = None

# Define the level data for this level's primary sections.
class Level13_main(levelgenerator.LevelData):
    # Create the level data for the primary sections.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome + biome_music_suffix)

# Define the level data for the fake underground section of the level.
class Level13_fake_underground(levelgenerator.LevelData):
    # Create the level data for the primary sections.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome + biome_music_suffix)

        # Play the Lego Yoda death sound effect until the player dies, by
        # which point it should abruptly stop for comedic effect.
        self.yoda_sound = eng.create_sound("lostlevels/assets/audio/objects/lego_yoda_death.ogg")
        self.yoda_sound.volume = 1
        self.yoda_sound.play()

    # Stop playing the Yoda sound effect when the player dies.
    def player_killed(self):
        self.yoda_sound.stop()

    # Stop playing the Yoda sound effect when the level ends.
    def level_finish(self):
        self.yoda_sound.stop()

# Define the level data for the boss fight section of the level.
class Level13_bossfight(levelgenerator.LevelData):
    # Create the level data for the Goombas section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Do not play the level music. Play the Super Mario Advance 4 Bowser fight
        # music to start with.
        self.boss_music = eng.create_sound("lostlevels/assets/audio/sma4_boss_fight.ogg")
        self.boss_music.volume = 1
        if eng.find_gvar("music").get():
            self.boss_music.play(True)

        # Bind the boss entity to this level data instance.
        self.boss = None
        self.boss_killed = False

        # Bind the end-of-map wall to this level data instance.
        self.wall = None

        # Manage the boxing glove entity.
        self.boxing_glove = None

    # Stop playing the boss music when the player dies.
    def player_killed(self):
        self.boss_music.stop()

    # Stop playing the boss music when the level ends.
    def level_finish(self):
        self.boss_music.stop()

    # Manage certain obstacles.
    def per_frame(self):
        # Check for when the boss dies in order to decide when to start playing the actual level music.
        if self.boss.deleted and not self.boss_killed and self._level.player.alive:
            # Stop playing boss music.
            self.boss_killed = True
            self.boss_music.stop()
            self._level.play_music(self.biome + biome_music_suffix)

            # Remove the map scrolling limit.
            self._level.max_scroll = -1
            for ent in self.wall:
                self._engine.delete_entity(ent)

        # When the player proceeds from the boss fight, send a boxing glove that will punch the player
        # into the void.
        if not self.boxing_glove and self._level.player.get_baseorigin().x > 800:
            # Create the boxing glove.
            self.boxing_glove = self._engine.create_entity_by_class("sprite")
            self.boxing_glove.load("lostlevels/assets/sprites/boxing_glove.png", (180, 100), 1)
            self.boxing_glove.movetype = engine.entity.MOVETYPE_CUSTOM
            self.boxing_glove.velocity.x = 1000
            self.boxing_glove.set_baseorigin(pygame.math.Vector2(620, 
                                                                 self._level.player.get_baseorigin().y))

            # Create the collision function for the glove.
            def glove_collisionfinal(ent, other, coltype, coldir):
                # If this is not the glove colliding, continue.
                if coltype != engine.entity.COLTYPE_COLLIDING:
                    return
                
                # If the other entity is not the player, continue.
                if other.get_class() != "player":
                    return
                
                # Punch whatever the entity has been hit out of orbit.
                other.velocity = pygame.math.Vector2(ent.velocity.x, other.velocity.y + 450)
                ent.velocity.x = 0

                # Play a punching sound effect.
                punch = ent._engine.create_sound("lostlevels/assets/audio/objects/punch.ogg")
                punch.volume = 1
                punch.play()

            self.boxing_glove.get_event("collisionfinal").set_func(glove_collisionfinal)

# Define the level data for the Coldplay - Higher Power section of the level.
class Level13_higherpower(levelgenerator.LevelData):
    # Create the level data for the Coldplay - Higher Power section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music to start with. 
        level.play_music(biome + biome_music_suffix)

        # Create a sound instance for the Coldplay - Higher Power song to play later.
        self.higher_power_song = eng.create_sound("lostlevels/assets/audio/coldplay_higher_power.ogg")
        self.higher_power_song.volume = 1

        # Bind the Chris Martin entity to this level data instance.
        self.chris_martin = None
        self.higher_power_achieved = False

        # Used to track the furthest point up to which the world exists.
        self.max_world_x = 1280

        # Keep track of the section's level generator.
        self.gen = None

        # Manage the music video.
        self.music_video_frames = []
        self.music_video_index = 0
        self.music_video_last_timestamp = 0
        for i in range(0, coldplay_higher_power_frame_count):
            frame = eng.create_ui_element_by_class("image")
            frame.load(f"lostlevels/assets/sprites/coldplay_higher_power/frame-{(i + 1):03d}.png")
            frame.set_size(engine.ui.UDim2(1, 0, 1, 0))
            self.music_video_frames.append(frame)

    # Stop playing Coldplay - Higher Power when the player dies.
    def player_killed(self):
        self.higher_power_song.stop()

    # Stop playing Coldplay - Higher Power when the level ends.
    def level_finish(self):
        self.higher_power_song.stop()

    # Manage Chris Martin.
    def post_physics(self):
        # Have we achieved the higher power?
        if self.higher_power_achieved:
            # Have Chris Martin carry the player if the player is alive.
            if self._level.player.alive:
                self._level.player.set_baseorigin(self.chris_martin.get_baseorigin()
                                                  + pygame.math.Vector2(-20, 10))

            # Generate more of the world if we are nearing the furthest point up to
            # which the world currently exists.
            while self.max_world_x - self._level.player.get_baseorigin().x < 800:
                # Generate new scenery.
                self.gen.generate_ground(pygame.math.Vector2(self.max_world_x, -416), 40, 2)
                if random.randint(0, 2) < 2:
                    self.gen.generate_cloud(pygame.math.Vector2(
                                                self.max_world_x + random.randint(0, 320), 
                                                -96 - random.randint(0, 1) * 32),
                                            random.randint(2, 10))
                if random.randint(0, 2) < 2:
                    self.gen.generate_bush(pygame.math.Vector2(
                                               self.max_world_x + random.randint(0, 320), 
                                               -384),
                                           random.randint(2, 10))

                # Increment the max world x-coordinate value by 576 (32 * 18).
                self.max_world_x += 576

            # Increment the music video frame counter at 24 FPS, if showing.
            if self.music_video_last_timestamp > 0 and self._level.player.alive:
                frame_increment = int((time.perf_counter() - self.music_video_last_timestamp) / (1 / 24))
                if frame_increment > 0:
                    self.music_video_frames[self.music_video_index].enabled = False
                    self.music_video_index = ((self.music_video_index + frame_increment) 
                                            % len(self.music_video_frames))
                    self.music_video_frames[self.music_video_index].enabled = True
                    self.music_video_last_timestamp += frame_increment * (1 / 24)

        else:
            # Have Chris Martin look at the player if the higher power has
            # not been achieved.
            self.chris_martin.flip(self.chris_martin.get_centre().x - self._level.player.get_centre().x
                                   > 0)

    # Achieve the higher power.
    def achieve_higher_power(self):
        global biome_music_suffix

        # Continue if the higher power has already been achieved.
        if self.higher_power_achieved:
            return

        # Enable higher power mode.
        self.higher_power_achieved = True
        biome_music_suffix = "_coldplay"

        # Make Chris Martin start sprinting at a very fast speed.
        self.chris_martin.flip(False)
        self.chris_martin.move = 5000

        # Disable the player's movement.
        self._level.player.moveable = False
        self._level.player.index = 4
        self._level.player.move = 0
        self._level.player.velocity = pygame.math.Vector2(0, 0)
        self._level.player.movetype = engine.entity.MOVETYPE_NONE
        self._level.player.flip(False)

        # Turn off the current level music and play Coldplay's Higher Power, if
        # the music gvar is enabled.
        if self._engine.find_gvar("music").get():
            self._level.stop_music()
            self.higher_power_song.play(True)

        # Time the transition point to when we show the actual music video for
        # Coldplay's Higher Power.
        self._engine.create_timer(Level13_higherpower.show_higher_power_video, 4.35, self)
        self._engine.create_timer(Level13_higherpower.kill_player, 9.05, self)

    # Show the music video for Coldplay - Higher Power.
    def show_higher_power_video(self):
        # Check that the first video frame still exists.
        if self.music_video_frames[0].deleted:
            return
        
        # Check that the player is stil alive.
        if not self._level.player.alive:
            return

        # Create a flash bang that gradually fades.
        effects.create_flash_bang(self._engine, 8)

        # Begin showing the music video.
        self.music_video_frames[0].enabled = True
        self.music_video_last_timestamp = time.perf_counter()

        # Slow down Chris Martin so that the player observes him leaving the
        # screen for a longer duration after dying.
        self.chris_martin.acceleration = 6.5
        self.chris_martin.move = 750
        self.chris_martin.velocity = pygame.math.Vector2(0, 0)

    # Stop showing Coldplay's Higher Power and kill the player.
    def kill_player(self):
        # Check that the first video frame still exists.
        if self.music_video_frames[0].deleted:
            return
        
        # Check that the player is stil alive.
        if not self._level.player.alive:
            return

        # Stop the music video and kill the player.
        self.music_video_frames[self.music_video_index].enabled = False
        self.higher_power_song.stop()
        self._level.death()

        # Put some text making a reference to Coldplay's earlier alt-rock,
        # A Rush of Blood to the Head.
        text = self._engine.create_ui_element_by_class("text")
        text.load_localfont("lostlevels/assets/fonts/nes.ttf")
        text.set_colour(pygame.Color(255, 255, 255))
        text.set_size(engine.ui.UDim2(1, 0, 0, 50))
        text.set_position(engine.ui.UDim2(0, 0, 1, -130))
        text.set_text(f"BLAME IT UPON A RUSH OF BLOOD TO THE HEAD...")
        text.set_x_align(engine.ui.X_CENTRE)
        text.set_y_align(engine.ui.Y_CENTRE)
        text.enabled = True

# Define the level data for the Goombas section of the level.
class Level13_goombas(levelgenerator.LevelData):
    # Create the level data for the Goombas section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome + biome_music_suffix)

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
            self.train.get_event("collision").set_func(lambda ent, other, coltype, coldir:
                                                       sample_hooks.boulder_hit(ent, other, coltype))
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
def load_leveldata(eng: engine.LLEngine, 
                   level: lostlevels.scenes.Level, 
                   section: str, 
                   first_life: bool, 
                   first_load: bool):
    global biome_music_suffix
    global holding_key
    global world_1_1_module

    # Extract the biome and section information from the section name. Verify the
    # biome given and create the level generator using the biome's name. If there 
    # is no delimiter, assume that the biome is winter.
    split = section.split("_", 1)
    if len(split) == 2:
        biome, name = split
    else:
        biome, name = "winter", split[0]
    
    # Only create the level generator if we are not forwarding level generation to
    # the world 1-1 module.
    gen = levelgenerator.LevelGenerator(eng, level, biome)

    # If this is the player's first life playing this level, reset the biome music
    # suffix.
    if first_life:
        biome_music_suffix = ""

    # If this is not the player's first life playing this level and the higher
    # power has been achieved, replace the player's death sound with a snippet
    # of Coldplay's Fix You.
    elif biome_music_suffix == "_coldplay":
        level.player.death_sound = eng.create_sound("lostlevels/assets/audio/player/death_coldplay.ogg")
        level.player.death_sound.volume = 1

    # If the level has loaded for the first time for the player's current life,
    # reset the holding key counter.
    if first_load:
        holding_key = False

    # Preload the world 1-1 module.
    if world_1_1_module == None:
        world_1_1_module = lostlevels.scenes.LoadingLevel.load_level_module(1, 1)

    # Nested function for creating the SMB2 key that the player can hold.
    def create_smb2_key(hold = False, before_entity = None):
        # Create a key that the player can "use".
        key = eng.create_entity_by_class("sprite", before_entity)
        key.load("lostlevels/assets/sprites/smb2_key.png", (28, 32), 1)
        key.set_baseorigin(pygame.math.Vector2(274, -392))
        key.can_use = True

        # SMB2 key: follow the player.
        def key_follow_player():
            # Have the key follow the player.
            if abs(level.player.velocity.x) > 0.1:
                key.flip(level.player.velocity.x < 0)
            vertical_offset = 30 if level.player.index >= 1 and level.player.index <= 2 else 32
            key.set_baseorigin(level.player.get_baseorigin() + pygame.math.Vector2(-2, vertical_offset))

            # Toggle the visibility of the key.
            key.draw = level.player.draw

        # SMB2 key: upon using, set its per_frame event so that the key 
        # follows the player.
        def key_use():
            global holding_key
            key.movetype = engine.entity.MOVETYPE_NONE
            key.get_event("per_frame").set_func(lambda self: key_follow_player())
            key.can_use = False
            holding_key = True

        # Should the player hold the key by default?
        if hold:
            key_use()

        # Bind the key's USE function to key_use() so that the player has 
        # to equip the key manually.
        else:
            key.get_event("use").set_func(lambda self: key_use())

    # Is this the main section?
    if name == "1.3.main":
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
        pipe_sections = [
            ("overground_1.3.main", None),
            ("overground_smb2", None),
            (f"{biome}_bossfight", None),
            ("nowhere", None),
            (f"{biome}_higherpower", None),
            (f"{biome}_goombas", None),
            (f"1.1.main", None),
            (f"{biome}_goombas", None)
        ]
        for i in range(0, 8):
            # Create the pipe for the given index.
            gen.generate_pipe_body(pygame.math.Vector2(64 + i * 64, -384))
            pipe_top = gen.generate_pipe_top(pygame.math.Vector2(64 + i * 64, -352), 
                                             section = pipe_sections[i][0], 
                                             player_offset = pipe_sections[i][1])
            
            # If this is the 4th pipe, do not have it teleport the player to another section.
            # Instead, misguide the player by sending them upwards.
            if i == 3:
                def pipe_transport():
                    level.player.moveable = False
                    level.player.set_baseorigin(pygame.math.Vector2(52, 200))
                    level.player.velocity = pygame.math.Vector2(0, 600)
                for ent in pipe_top:
                    ent.get_event("entered").set_func(lambda self: eng.create_timer(pipe_transport, 0))

            # If this is the 5th pipe, hook its entered event so that all the frames for the
            # cropped section of Coldplay's Higher Power music video are preloaded while the 
            # player enters the pipe.
            elif i == 4 and not preloaded_coldplay_higher_power:
                def load_frames():
                    for i in range(0, coldplay_higher_power_frame_count):
                        engine.ui.Image.preload(
                            f"lostlevels/assets/sprites/coldplay_higher_power/frame-{(i + 1):03d}.png")
                    return engine.Event.DETOUR_CONTINUE
                for ent in pipe_top:
                    ent.get_event("entered").hook(lambda self, name, returnValue: load_frames(), True)

        # Create a wall after the pipes so that the player cannot walk out of the map.
        gen.generate_blocks(pygame.math.Vector2(576, 0), height = 15)

        # Create a funny cloud that will only be reachable by taking a malicious pipe.
        gen.generate_funny_cloud(pygame.math.Vector2(240, -64), spiked = True)

        # Return the level data generated for this section.
        return data
    
    # Is this the "SMB2" section?
    elif name == "smb2":
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

        # Add a fake SMB2-like door that leads to a fake underground section
        door = eng.create_entity_by_class("sprite", eng.entity_head())
        door.load("lostlevels/assets/sprites/smb2_door.png", (32, 64), 1)
        door.movetype = engine.entity.MOVETYPE_NONE
        door.set_baseorigin(pygame.math.Vector2(992, -352))
        door.can_use = holding_key
        door.use_dist = 10

        # SMB2 door: open the door if the player has the key.
        def door_use():
            global holding_key

            # Load the fake underground section after 1.5 seconds.
            def load_newsection():
                # Check that the door entity still exists.
                if door.deleted:
                    return
                
                # Check that the player is stil alive.
                if not level.player.alive:
                    return
                
                # Load the new level section.
                level.load_newlevel("underground_fake_underground", 
                                    pygame.math.Vector2(64, -350), 
                                    level.time_remaining)

            # Untoggle the holding key counter.
            holding_key = False

            # Create a 1.5-second timer for loading the fake underground section.
            level.player.can_die = False
            eng.delete_entity(level.player)
            eng.create_timer(load_newsection, 1.5)

            # Hide the door to create the impression it has been opened.
            door.draw = False

            # Play a sound effect for entering the door.
            door_sound = eng.create_sound("lostlevels/assets/audio/objects/door_open.ogg")
            door_sound.volume = 1
            door_sound.play()
        door.get_event("use").set_func(lambda self: door_use())

        # Add a fake SMB2-like hill to accompany the door.
        smb2 = eng.create_entity_by_class("sprite", eng.entity_head())
        smb2.load("lostlevels/assets/sprites/smb2_hill.png", (256, 352), 1)
        smb2.movetype = engine.entity.MOVETYPE_NONE
        smb2.set_baseorigin(pygame.math.Vector2(860, -128))

        # Add an invisible platform so that the player can stand on the hill.
        gen.generate_rope(pygame.math.Vector2(860, -128), 8, False)

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
        
        # If the player came out of the jar section pipe with a key, spawn a 1996 Stock train 
        # and the key.
        if holding_key:
            # Spawn the train.
            train = eng.create_entity_by_class("sprite")
            train.movetype = engine.entity.MOVETYPE_CUSTOM
            train.load("lostlevels/assets/sprites/1996_stock.png", (6908, 158), 1)
            train.velocity.x = 1200
            train.game_flags |= lostlevels.sprites.DO_NOT_DELETE
            train.set_baseorigin(pygame.math.Vector2(-7600, -258))
            train.get_event("collision").set_func(lambda ent, other, coltype, coldir:
                                                  sample_hooks.boulder_hit(ent, other, coltype))
            eng.activate_entity(train)

            # Play the 1996 Stock sound effect.
            motors = eng.create_sound("lostlevels/assets/audio/objects/1996_stock_rolling.ogg")
            motors.volume = 1
            motors.play()

            # Spawn the key.
            create_smb2_key(True, None)

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
                              "overground_smb2", pygame.math.Vector2(596, -230))
        
        # Create a key that the player can "use".
        create_smb2_key(holding_key, body[0])

        # Return the level data generated for this section.
        return data

    # Is this the fake underground section afer opening the "SMB2" door?
    elif name == "fake_underground":
        # Create the level data for this section.
        data = Level13_fake_underground(eng, level, pygame.math.Vector2(276, -64), biome)

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Force the player to fall at a fast speed.
        level.player.velocity = pygame.math.Vector2(0, -400)

        # Return the level data generated for this section.
        return data

    # Is this the boss fight setion?
    elif name == "bossfight":
        # Create the level data for this section.
        data = Level13_bossfight(eng, level, pygame.math.Vector2(52, 0), biome)

        # Initially stop the map from scrolling.
        level.max_scroll = 0

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 40, 2)

        # Create the boss.
        boss = eng.create_entity_by_class("dr_house")
        boss.set_baseorigin(pygame.math.Vector2(416, 0))
        boss.level = level
        data.boss = boss

        # Create a temporary wall that prevents the player from running from the boss.
        data.wall = gen.generate_ground(pygame.math.Vector2(576, 0), height = 15)

        # Return the level data generated for this section.
        return data

    # Is this the Coldplay - Higher Power section?
    elif name == "higherpower":
        # Can anybody fly this thing?

        # Create the level data for this section.
        data = Level13_higherpower(eng, level, pygame.math.Vector2(52, 0), biome)

        # Bind the level generator to the level data object.
        data.gen = gen

        # Create a pipe that the player will "fall" out of as they spawn.
        pipe = gen.generate_pipe_body(pygame.math.Vector2(32, 0), orientation = lostlevels.sprites.PIPE_180)
        pipe.extend(gen.generate_pipe_top(pygame.math.Vector2(32, -32), lostlevels.sprites.PIPE_180))
        for piece in pipe:
            piece.movetype = engine.entity.MOVETYPE_NONE

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 40, 2)

        # Create some scenery.
        gen.generate_bush(pygame.math.Vector2(160, -384), 10)
        gen.generate_funny_cloud(pygame.math.Vector2(96, -96), spiked = True)
        gen.generate_cloud(pygame.math.Vector2(288, -64), 5)

        # Create Chris Martin.
        chris_martin = eng.create_entity_by_class("animated_character")
        chris_martin.load("lostlevels/assets/sprites/chris_martin.png", (24, 65), 4)
        chris_martin.set_baseorigin(pygame.math.Vector2(800, -351))
        chris_martin.acceleration = 1
        data.chris_martin = chris_martin

        # Chris Martin: achieve higher power if the player interacts with him.
        def chris_martin_func(self, name, returnValue, other, coltype, coldir):
            # If the other entity is not a player, continue.
            if other.get_class() != "player":
                return engine.Event.DETOUR_CONTINUE

            # Achieve higher power and continue.
            data.achieve_higher_power()
            return engine.Event.DETOUR_CONTINUE

        # Hook chris_martin_func() to Chris Martin's collision event.
        chris_martin.get_event("collision").hook(chris_martin_func)

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

    # The 7th pipe may've been used, so forward all remainder section loading code to the world 1-1
    # module.
    else:
        return world_1_1_module.load_leveldata(eng, level, section, first_life, first_load)