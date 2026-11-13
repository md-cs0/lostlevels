"""World 1-3."""

import random
import time
import math
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

# Store information about the 2nd pipe section key.
holding_key = False
has_used_key = False

# Has the player unlocked the 8th pipe section door?
unlocked_cave_door = False

# Due to the way the module is named, the world 1-1 module must be loaded dynamically.
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
            self.boxing_glove.set_baseorigin(
                pygame.math.Vector2(620, self._level.player.get_baseorigin().y))

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
            # TODO: nothing specific to change with this code for now, however the scorebar
            # currently appears on top of this. This will be corrected in the future when
            # I get around writing biome-specific modules.
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

        # Log the achieving of higher power. If the user keeps an eye on their
        # console, this should serve as a hint of the alternative exit for this
        # level.
        self._engine.console.log(
            "[Lost Levels]: higher power unlocked, new features of world 1-3 unlocked")

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
        self.music_video_frames[self.music_video_index].enabled = True
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
        self._level.player.movetype = engine.entity.MOVETYPE_PHYSICS

        # Put some text making a reference to Coldplay's earlier alt-rock,
        # A Rush of Blood to the Head.
        text = self._engine.create_ui_element_by_class("text")
        text.load_localfont("lostlevels/assets/fonts/nes.ttf")
        text.set_colour(pygame.Color(255, 255, 255, 255))
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

# Define the level data for the inside cave section of the level.
class Level13_cave(levelgenerator.LevelData):
    # Fighting stages.
    FIGHT_PRELOADING                = -1
    FIGHT_WAITING_INPUT             = 0
    FIGHT_SELECTING_ENEMY           = 1
    FIGHT_SELECTING_ACTION          = 2
    FIGHT_REMEMBERING_HOW_TO_SPEAK  = 3
    FIGHT_COMBAT                    = 4
    FIGHT_BACK_TO_WAITING_INPUT     = 5
    FIGHT_SINGING                   = 6
    FIGHT_ENDED                     = 7

    # Create the level data for the Goombas section.
    def __init__(self, eng, level, player_offset, biome):
        # Call the LevelData constructor.
        super().__init__(eng, level, player_offset, biome)

        # Play the level music. 
        level.play_music(biome + biome_music_suffix)

        # Keep track of some of the generated world.
        self.ground = None
        self.trees = None
        self.cached_time_remaining = 0

        # Manage Seymour Skinner's introduction.
        self.seymour = None
        self.fade_in = None
        self.seymour_speech_tick = 0
        self.fight_sequence_triggered = False
        self.seymour_speech = self._engine.create_sound("lostlevels/assets/audio/objects/seymour.ogg")
        self.seymour_speech.volume = 1
        self.seymour_dialogue = self._engine.create_ui_element_by_class("image")
        self.seymour_dialogue.load("lostlevels/assets/sprites/seymour_skinner_speech.png")
        self.seymour_dialogue.set_size(engine.ui.UDim2(0, 492, 0, 152), False)
        self.seymour_dialogue.set_position(engine.ui.UDim2(0.5, -246, 0, 30))
        self.upper_dialogue_cover = self._engine.create_ui_element_by_class("frame")
        self.upper_dialogue_cover.set_size(engine.ui.UDim2(0, 250, 0, 20))
        self.upper_dialogue_cover.set_position(engine.ui.UDim2(0, 218, 0, 58))
        self.lower_dialogue_cover = self._engine.create_ui_element_by_class("frame")
        self.lower_dialogue_cover.set_size(engine.ui.UDim2(0, 250, 0, 20))
        self.lower_dialogue_cover.set_position(engine.ui.UDim2(0, 218, 0, 94))

        # Manage variables for the general fight.
        self.fight_started = False
        self.fight_state = self.FIGHT_PRELOADING
        self.fight_player_speech_tick = 0
        self.fight_background = None
        self.fight_asterisk = None
        self.fight_seymour = None
        self.fight_player_dialogue = None
        self.fight_player_upper_dialogue_cover = None
        self.fight_player_upper_dialogue_cover = None
        self.fight_left_bar = None
        self.fight_right_bar = None
        self.fight_top_bar = None
        self.fight_bottom_bar = None
        self.fight_timestamp_since_last_resize = 0
        self.fight_box_width = 511
        self.fight_player = None
        self.fight_beams = []
        self.fight_beams_tick = 0
        self.asgore_theme = self._engine.create_sound(
            "lostlevels/assets/audio/undertale_asgore_theme.ogg")
        self.asgore_theme.volume = 1

        # Manage variables for the singing bit.
        self.fight_can_sing = False
        self.fight_move_seymour = True
        self.fight_freeman = None
        self.fight_freeman_animation_timestamp = 0
        self.fight_flash_bang = None
        self.my_universe = self._engine.create_sound(
            "lostlevels/assets/audio/smb2jar_coldplay/main.ogg")
        self.my_universe.volume = 1
        self.explosion = self._engine.create_sound("lostlevels/assets/audio/objects/rocket_hit.ogg")
        self.explosion.volume = 1

    # Manage the Undertale-themed fight with Seymour Skinner.
    def per_frame(self):
        # Once the player reaches the trigger point, trigger the Undertale-themed fight
        # with Seymour.
        if not self.fight_sequence_triggered and self._level.player.get_baseorigin().x > 800:
            # Toggle the fight triggered counter.
            self.fight_sequence_triggered = True
            self.fight_triggered_timestamp = time.perf_counter()

            # Set the time limit to infinite and disable the scoreboard.
            self.cached_time_remaining = self._level.time_remaining
            self._level.time_remaining = math.inf
            self._level.toggle_scoreboard(False)

            # Stop the player from moving.
            self._level.player.moveable = False
            self._level.player.move = 0
            self._level.player.always_animate = True

            # Play Seymour's speech, accompanied by Toby Fox's Imminent Death from
            # Deltarune, and stop playing the level's music.
            self.seymour_speech.play(True)
            self._level.stop_music()
            self._engine.create_timer(Level13_cave.manage_seymour_speech, 0.59, self)

        # Handle the actual fight.
        elif self.fight_started and self.fight_state != self.FIGHT_ENDED:
            # Toggle whether to draw the player based on whether the player is engaging in
            # combat.
            self.fight_player.draw = (self.fight_state == self.FIGHT_COMBAT)

            # Move Seymour around.
            if self.fight_move_seymour:
                timestamp = time.perf_counter()
                last_x = self.fight_seymour.get_position().x.offset
                new_x = -38 + math.sin(timestamp * 2) * 10
                self.fight_seymour.set_position(engine.ui.UDim2(
                    0.5, new_x, 0, 35 + math.sin(timestamp * 4) * 10))
                self.fight_seymour.flip(new_x - last_x > 0)

            # Maintain the size of the box.
            timestamp = time.perf_counter()
            if timestamp - self.fight_timestamp_since_last_resize > 1 / 60:
                # Resize the box.
                bar_width = self.fight_top_bar.get_hitbox().x
                if self.fight_box_width > bar_width:
                    new_bar_width = min(self.fight_box_width - 10, 
                                        self.fight_top_bar.get_hitbox().x + 15)
                else:
                    new_bar_width = max(self.fight_box_width - 10, 
                                        self.fight_top_bar.get_hitbox().x - 15)
                self.fight_top_bar.set_hitbox(pygame.math.Vector2(new_bar_width, 5))
                self.fight_top_bar.set_baseorigin(pygame.math.Vector2(
                    37 + self._level.camoffset + (250 - new_bar_width / 2), -250))
                self.fight_bottom_bar.set_hitbox(pygame.math.Vector2(new_bar_width, 5))
                self.fight_bottom_bar.set_baseorigin(pygame.math.Vector2(
                    37 + self._level.camoffset + (250 - new_bar_width / 2), -385))
                self.fight_left_bar.set_baseorigin(pygame.math.Vector2(
                    32 + self._level.camoffset + (250 - new_bar_width / 2), -250))
                self.fight_right_bar.set_baseorigin(pygame.math.Vector2(
                    537 + self._level.camoffset - (250 - new_bar_width / 2), -250))
                self.fight_timestamp_since_last_resize = timestamp

            # Are we in combat mode?
            if self.fight_state == self.FIGHT_COMBAT:
                # Handle heart movement.
                key_dict = self._level.get_keys_dict()
                vel_x = 0
                vel_y = 0
                multiplier = 0.5 if key_dict[pygame.K_LSHIFT] else 1
                if key_dict[pygame.K_LEFT]:
                    vel_x -= 120 * multiplier
                if key_dict[pygame.K_RIGHT]:
                    vel_x += 120 * multiplier
                if key_dict[pygame.K_UP]:
                    vel_y += 120 * multiplier
                if key_dict[pygame.K_DOWN]:
                    vel_y -= 120 * multiplier
                self.fight_player.velocity = pygame.math.Vector2(vel_x, vel_y)

            # Are we transitioning back to the waiting for input state?
            elif (self.fight_state == self.FIGHT_BACK_TO_WAITING_INPUT
                  and self.fight_top_bar.get_hitbox().x == self.fight_box_width - 10):
                # Show the player dialogue again.
                self.manage_player_speech(20, 10)
                self.fight_asterisk.enabled = True
                self.fight_player_dialogue.enabled = True

                # Change the state to the waiting for input state.
                self.fight_state = self.FIGHT_WAITING_INPUT

                # Select the ACT button.
                self.fight_background.load("lostlevels/assets/sprites/seymour_skinner_encounter.png")
                self.fight_background.set_size(engine.ui.UDim2(1, 0, 1, 0))

            # Is the player singing?
            elif self.fight_state == self.FIGHT_SINGING:
                # Animate the player's character until the player gets
                # close to Seymour, then stop the character.
                timestamp = time.perf_counter()
                if (timestamp - self.fight_freeman_animation_timestamp > 0.15
                    and self.fight_freeman.velocity.x > 0):
                    self.fight_freeman_animation_timestamp = timestamp
                    self.fight_freeman.index = (self.fight_freeman.index + 1) % 2
                if self.fight_freeman.get_baseorigin().x > self._level.camoffset + 125:
                    self.fight_freeman.velocity = pygame.math.Vector2(0, 0)
                    self.fight_freeman.set_baseorigin(
                        pygame.math.Vector2(self._level.camoffset + 125, -152))
                    self.fight_freeman.index = 0

            # Clear any beams that have long left the screen.
            for beam in self.fight_beams:
                if beam.get_topleft().x > self._level.camoffset + 576 or beam.get_bottomleft().y > 0:
                    self._engine.delete_entity(beam)
            self.fight_beams[:] = [beam for beam in self.fight_beams if beam.draw]

    # Manage Seymour's speech dialogue.
    def manage_seymour_speech(self):
        # Ensure the speech dialogue is enabled.
        self.seymour_dialogue.enabled = True
        self.upper_dialogue_cover.enabled = True
        self.lower_dialogue_cover.enabled = True

        # Move the black bars out of the way to reveal another character of the speech
        # dialogue.
        self.seymour_speech_tick += 1
        self.upper_dialogue_cover.set_position(engine.ui.UDim2(
            0, 218 + self.seymour_speech_tick * 16, 0, 58))
        self.upper_dialogue_cover.set_size(engine.ui.UDim2(
            0, 250 - self.seymour_speech_tick * 16, 0, 20))
        self.lower_dialogue_cover.set_position(engine.ui.UDim2(
            0, 218 + max(0, (self.seymour_speech_tick - 15) * 16), 0, 94))
        self.lower_dialogue_cover.set_size(engine.ui.UDim2(
            0, 250 - max(0, (self.seymour_speech_tick - 15) * 16), 0, 20))

        # Call this method again later to reveal more of the speech dialogue, until the
        # entire dialogue has been revealed.
        if self.seymour_speech_tick < 35:
            self._engine.create_timer(Level13_cave.manage_seymour_speech, 0.15, self)

        # After some time, hide the dialogue and set a timer for the main fighting
        # sequence.
        else:
            self.seymour_dialogue.enabled = False
            self.upper_dialogue_cover.enabled = False
            self.lower_dialogue_cover.enabled = False
            self._engine.create_timer(Level13_cave.initialise_fight, 2, self)

    # Initialise the fighting sequence before launching the player straight into the
    # fight.
    def initialise_fight(self):
        # Hide parts of the visible world and anchor the player.
        for ent in self.ground:
            ent.draw = False
        self.trees.draw = False
        self._level.player.movetype = engine.entity.MOVETYPE_NONE

        # Stop playing the track accompanying Seymour's introduction.
        self.seymour_speech.stop()

        # Uncover the fog.
        self._fog.enabled = False

        # Play the Undertale heart shattering sound effect.
        shatter = self._engine.create_sound(
            "lostlevels/assets/audio/objects/undertale_heart_shatter.ogg")
        shatter.volume = 1
        shatter.play()

        # Time the "eye flash" effect.
        self._engine.create_timer(Level13_cave.eye_flash, 1.5, self)

    # "Eye flash" effect immediately prior to the fight.
    def eye_flash(self):
        # Play the eye flash sound effect.
        flash = self._engine.create_sound("lostlevels/assets/audio/objects/undertale_eye_flash.ogg")
        flash.volume = 1
        flash.play()

        # Create a fade-in effect that transitions into the fight.
        self.fade_in = effects.create_fade_in_screen(self._engine, 50)

        # Time the beginning of the fight.
        self._engine.create_timer(Level13_cave.start_fight, 1.5, self)

    # Begin the Undertale-themed fight against Seymour.
    def start_fight(self):
        # Hide the player and Seymour sprites and delete the fade-in UI element.
        self._engine.delete_ui_element(self.fade_in)
        self._level.player.draw = False
        self.seymour.draw = False 

        # Start playing ASGORE's theme.
        self.asgore_theme.play(True)

        # Create the background for the fight. These use rectangle entities for
        # handling basic collision with the player.
        self.fight_background = self._engine.create_ui_element_by_class("image", 
                                                                        engine.ui.LAYER_BACKGROUND)
        self.fight_background.load("lostlevels/assets/sprites/seymour_skinner_encounter.png")
        self.fight_background.set_size(engine.ui.UDim2(1, 0, 1, 0))
        self.fight_background.enabled = True
        self.fight_asterisk = self._engine.create_ui_element_by_class("image")
        self.fight_asterisk.load("lostlevels/assets/sprites/undertale_asterisk.png")
        self.fight_asterisk.set_size(engine.ui.UDim2(0, 16, 0, 10))
        self.fight_asterisk.set_position(engine.ui.UDim2(0, 52, 0, 282))
        self.fight_asterisk.enabled = True
        self.fight_seymour = self._engine.create_ui_element_by_class("image")
        self.fight_seymour.load("lostlevels/assets/sprites/seymour_skinner_undertale_full.png")
        self.fight_seymour.set_size(engine.ui.UDim2(0, 75, 0, 192))
        self.fight_seymour.set_position(engine.ui.UDim2(0.5, -38, 0, 35))
        self.fight_seymour.enabled = True
        self.fight_player_dialogue = self._engine.create_ui_element_by_class("image")
        self.fight_player_dialogue.load("lostlevels/assets/sprites/player_undertale_speech.png")
        self.fight_player_dialogue.set_size(engine.ui.UDim2(0, 317, 0, 58))
        self.fight_player_dialogue.set_position(engine.ui.UDim2(0, 84, 0, 278))
        self.fight_player_dialogue.enabled = True
        self.fight_left_bar = self._engine.create_entity_by_class("rect")
        self.fight_left_bar.colour = pygame.Color(255, 255, 255, 255)
        self.fight_left_bar.set_hitbox(pygame.math.Vector2(5, 140))
        self.fight_left_bar.set_baseorigin(pygame.math.Vector2(32 + self._level.camoffset, -250))
        self.fight_left_bar.movetype = engine.entity.MOVETYPE_CUSTOM
        self.fight_right_bar = self._engine.create_entity_by_class("rect")
        self.fight_right_bar.colour = pygame.Color(255, 255, 255, 255)
        self.fight_right_bar.set_hitbox(pygame.math.Vector2(5, 140))
        self.fight_right_bar.set_baseorigin(pygame.math.Vector2(537 + self._level.camoffset, -250))
        self.fight_right_bar.movetype = engine.entity.MOVETYPE_CUSTOM
        self.fight_top_bar = self._engine.create_entity_by_class("rect")
        self.fight_top_bar.colour = pygame.Color(255, 255, 255, 255)
        self.fight_top_bar.set_hitbox(pygame.math.Vector2(501, 5))
        self.fight_top_bar.set_baseorigin(pygame.math.Vector2(37 + self._level.camoffset, -250))
        self.fight_top_bar.movetype = engine.entity.MOVETYPE_CUSTOM
        self.fight_bottom_bar = self._engine.create_entity_by_class("rect")
        self.fight_bottom_bar.colour = pygame.Color(255, 255, 255, 255)
        self.fight_bottom_bar.set_hitbox(pygame.math.Vector2(501, 5))
        self.fight_bottom_bar.set_baseorigin(pygame.math.Vector2(37 + self._level.camoffset, -385))
        self.fight_bottom_bar.movetype = engine.entity.MOVETYPE_CUSTOM
        self.manage_player_speech(20, 10)

        # Construct the rest of the fight UI that shouldn't be visible yet.
        self.fight_player_enemy_select = self._engine.create_ui_element_by_class("image")
        self.fight_player_enemy_select.load(
            "lostlevels/assets/sprites/player_undertale_enemy_select.png")
        self.fight_player_enemy_select.set_size(engine.ui.UDim2(0, 304, 0, 26))
        self.fight_player_enemy_select.set_position(engine.ui.UDim2(0, 64, 0, 276))
        self.fight_player_act_select = self._engine.create_ui_element_by_class("image")
        self.fight_player_act_select.load("lostlevels/assets/sprites/player_undertale_act_select.png")
        self.fight_player_act_select.set_size(engine.ui.UDim2(0, 127, 0, 26))
        self.fight_player_act_select.set_position(engine.ui.UDim2(0, 64, 0, 276))
        self.fight_player_remember_talk = self._engine.create_ui_element_by_class("image")
        self.fight_player_remember_talk.load(
            "lostlevels/assets/sprites/player_undertale_speech_talk.png")
        self.fight_player_remember_talk.set_size(engine.ui.UDim2(0, 412, 0, 60))
        self.fight_player_remember_talk.set_position(engine.ui.UDim2(0, 84, 0, 278))
        self.fight_player = self._engine.create_entity_by_class("sprite")
        self.fight_player.load("lostlevels/assets/sprites/undertale_soul.png", (16, 16), 1)
        self.fight_player.set_baseorigin(
            pygame.math.Vector2(279 + self._level.camoffset, -312))
        self.fight_player.draw = False
        self.fight_player.gravity = 0
        self.fight_player.friction = 0
        self.fight_player.identifier = "player_soul"
        self.fight_freeman = self._engine.create_entity_by_class("sprite")
        self.fight_freeman.load("lostlevels/assets/sprites/player_undertale_full.png", (24, 58), 2)
        self.fight_freeman.set_baseorigin(
            pygame.math.Vector2(-24 + self._level.camoffset, -152))
        self.fight_freeman.movetype = engine.entity.MOVETYPE_CUSTOM
        self.fight_freeman.draw = False

        # Toggle the fight started counter.
        self.fight_started = True
        self.fight_state = self.FIGHT_WAITING_INPUT

    # Manage the player's speech dialogue.
    def manage_player_speech(self, top_ticks, bottom_ticks, first_time = True):
        # If this is the first time, the bars need to be re-created so that they are 
        # on top of the current text.
        if first_time:
            self.fight_player_speech_tick = 0
            self.fight_player_upper_dialogue_cover = self._engine.create_ui_element_by_class("frame")
            self.fight_player_upper_dialogue_cover.set_size(engine.ui.UDim2(0, 425, 0, 30))
            self.fight_player_upper_dialogue_cover.set_position(engine.ui.UDim2(0, 84, 0, 278))
            self.fight_player_upper_dialogue_cover.enabled = True
            self.fight_player_lower_dialogue_cover = self._engine.create_ui_element_by_class("frame")
            self.fight_player_lower_dialogue_cover.set_size(engine.ui.UDim2(0, 425, 0, 30))
            self.fight_player_lower_dialogue_cover.set_position(engine.ui.UDim2(0, 84, 0, 312))
            self.fight_player_lower_dialogue_cover.enabled = True

        # Move the black bars out of the way to reveal another character of the speech
        # dialogue.
        self.fight_player_speech_tick += 1
        self.fight_player_upper_dialogue_cover.set_position(engine.ui.UDim2(
            0, 84 + self.fight_player_speech_tick * 16, 0, 278))
        self.fight_player_upper_dialogue_cover.set_size(engine.ui.UDim2(
            0, 425 - self.fight_player_speech_tick * 16, 0, 30))
        self.fight_player_lower_dialogue_cover.set_position(engine.ui.UDim2(
            0, 84 + max(0, (self.fight_player_speech_tick - top_ticks) * 16), 0, 312))
        self.fight_player_lower_dialogue_cover.set_size(engine.ui.UDim2(
            0, 425 - max(0, (self.fight_player_speech_tick - top_ticks) * 16), 0, 30))

        # Play a message sound effect after each character is revealed.
        message_sfx = self._engine.create_sound(
            "lostlevels/assets/audio/objects/undertale_message.ogg")
        message_sfx.volume = 1
        message_sfx.play()
        
        # Call this method again later to reveal more of the speech dialogue, until the
        # entire dialogue has been revealed.
        if self.fight_player_speech_tick < top_ticks + bottom_ticks:
            self._engine.create_timer(Level13_cave.manage_player_speech, 0.032, 
                                      self, 
                                      top_ticks, 
                                      bottom_ticks,
                                      False)
        else:
            self._engine.delete_ui_element(self.fight_player_upper_dialogue_cover)
            self._engine.delete_ui_element(self.fight_player_lower_dialogue_cover)

    # Play the select sound effect.
    def play_select_sfx(self):
        select_sfx = self._engine.create_sound(
            "lostlevels/assets/audio/objects/undertale_select.ogg")
        select_sfx.volume = 1
        select_sfx.play()

    # Handle user input.
    def keydown(self, enum, unicode, focused):
        # Ignore key inputs that aren't the space key.
        if enum != pygame.K_SPACE:
            return

        # Are we currently waiting for the player to choose how they will interact with
        # Seymour?
        if self.fight_state == self.FIGHT_WAITING_INPUT:
            # If the dialogue has not been fully read, uncover it fully first.
            if self.fight_player_speech_tick < 30:
                self.fight_player_speech_tick = 30
                return

            # Since the only option is to ACT, continue on to enemy selection.
            else:
                # Change the state to the selecting enemy state.
                self.fight_state = self.FIGHT_SELECTING_ENEMY

                # Update the UI.
                self.fight_asterisk.enabled = False
                self.fight_player_dialogue.enabled = False
                self.fight_player_enemy_select.enabled = True

                # Remove the heart icon from the ACT button.
                self.fight_background.load(
                    "lostlevels/assets/sprites/seymour_skinner_encounter_choosing_act.png")
                self.fight_background.set_size(engine.ui.UDim2(1, 0, 1, 0))

                # Play the input sound effect.
                self.play_select_sfx()

        # Are we currently waiting for the player to select an enemy?
        elif self.fight_state == self.FIGHT_SELECTING_ENEMY:
            # Change the state to the selecting action state.
            self.fight_state = self.FIGHT_SELECTING_ACTION

            # Update the UI.
            self.fight_player_enemy_select.enabled = False
            self.fight_player_act_select.enabled = True

            # Play the input sound effect.
            self.play_select_sfx()

        # Are we currently waiting for the player to select an action?
        elif self.fight_state == self.FIGHT_SELECTING_ACTION:
            # Is the player able to sing?
            if self.fight_can_sing:
                # Change the state to the singing state.
                self.fight_state = self.FIGHT_SINGING

                # Update the UI.
                self.fight_freeman.velocity = pygame.math.Vector2(75, 0)
                self.fight_freeman.draw = True

                # Start playing Coldplay - My Universe.
                self.my_universe.play()

                # Create timers for stopping ASGORE's theme, changing Seymour's 
                # emotion and making Seymour explode.
                self._engine.create_timer(lambda: self.asgore_theme.stop(), 2.3)
                self._engine.create_timer(Level13_cave.update_seymour_emotion, 3.0, self)
                self._engine.create_timer(Level13_cave.explode_seymour, 4.60, self)

            # Tell the player that they just remembered how to speak (referring to
            # Gordon Freeman being a silent protagonist).
            else:
                # Change the state to the remembering how to speak state.
                self.fight_state = self.FIGHT_REMEMBERING_HOW_TO_SPEAK
                self.fight_can_sing = True

                # Update the UI.
                self.fight_player_remember_talk.enabled = True
                self.fight_asterisk.enabled = True
                self.manage_player_speech(26, 11)

            # Disable the action selection UI.
            self.fight_player_act_select.enabled = False

            # Deselect the ACT button.
            self.fight_background.load(
                "lostlevels/assets/sprites/seymour_skinner_encounter_act_selected.png")
            self.fight_background.set_size(engine.ui.UDim2(1, 0, 1, 0))

            # Play the input sound effect.
            self.play_select_sfx()

        # Are we currently waiting for the player to respond to the remembering
        # how to speak prompt?
        elif self.fight_state == self.FIGHT_REMEMBERING_HOW_TO_SPEAK:
            # If the dialogue has not been fully read, uncover it fully first.
            if self.fight_player_speech_tick < 37:
                self.fight_player_speech_tick = 37
                return

            # Since the only option is to ACT, continue on to enemy selection.
            else:
                # Change the state to the combatting enemy state.
                self.fight_state = self.FIGHT_COMBAT

                # Update the UI.
                self.fight_asterisk.enabled = False
                self.fight_player_remember_talk.enabled = False

                # Resize the box.
                self.fight_box_width = 140

                # Create timers for Seymour's attack and going back to the waiting
                # for input state.
                self._engine.create_timer(Level13_cave.shoot_beams, 1.0, self)
                self._engine.create_timer(Level13_cave.finish_shooting_beams, 3.25, self)

                # Play the input sound effect.
                self.play_select_sfx()

    # Shoot some beams.
    def shoot_beams(self, first_time = True):
        # If the player entity is deleted, stop shooting beams.
        if not self._level.player.alive or self._level.player.deleted:
            return

        # Beam constructor.
        def create_beam(size, velocity, origin):
            # Beam: kill the player if the beam collides into them.
            def collision(self_beam, other, coltype, coldir):
                # If the other entity is not the player's soul, ignore collision.
                if other.identifier != "player_soul":
                    return False

                # Kill the player.
                self._level.death()

                # Ignore collision anyway so that the beam can continue flying.
                return False

            # Create the beam entity.
            beam = self._engine.create_entity_by_class("rect")
            beam.set_baseorigin(origin)
            beam.set_hitbox(size)
            beam.velocity = velocity
            beam.colour = pygame.Color(255, 255, 255, 255)
            beam.movetype = engine.entity.MOVETYPE_CUSTOM
            beam.get_event("collision").set_func(collision)
            self.fight_beams.append(beam)
            return beam

        # If this is the first time, reset the beams tick counter and create some beams.
        if first_time:
            # Reset the beams tick counter.
            self.fight_beams_tick = 0

            # Create a larger beam to catch out players who hide away in the left
            # half of the box.
            create_beam(pygame.math.Vector2(100, 100), 
                        pygame.math.Vector2(0, -2000),
                        pygame.math.Vector2(222 + self._level.camoffset, 100))

            # Create another larger beam to catch out players who hide away in the
            # bottom-right half of the box.
            create_beam(pygame.math.Vector2(100, 75), 
                        pygame.math.Vector2(2000, 0),
                        pygame.math.Vector2(-100 + self._level.camoffset, -310))

            # Play the Undertale Gaster Blaster sound effect.
            blaster = self._engine.create_sound(
                "lostlevels/assets/audio/objects/undertale_gaster_blaster.ogg")
            blaster.volume = 1
            blaster.play()

        # If the fight beams tick counter is between 2 and 22, shoot horizontal beams from
        # the left.
        if self.fight_beams_tick >= 2 and self.fight_beams_tick < 22:
            # On tick 2, play the Undertale rainbow beam sound effect.
            if self.fight_beams_tick == 2:
                beam = self._engine.create_sound(
                    "lostlevels/assets/audio/objects/undertale_rainbowbeam.ogg")
                beam.volume = 1
                beam.play()

            # Create the beam. 
            create_beam(pygame.math.Vector2(100, 10), 
                        pygame.math.Vector2(5000, -500),
                        pygame.math.Vector2(
                            -100 + self._level.camoffset, -215 - self.fight_beams_tick * 5))

        # If the fight beams tick counter is between 27 and 35, shoot beams from
        # below.
        elif self.fight_beams_tick >= 27 and self.fight_beams_tick < 35:
            create_beam(pygame.math.Vector2(10, 100), 
                        pygame.math.Vector2(0, 5000),
                        pygame.math.Vector2(
                            222 + self._level.camoffset + (self.fight_beams_tick - 27) * 10, -480))

        # If the fight beams tick counter is 39, shoot a final beam from below
        # right at right-most corner of the box to trick the player.
        elif self.fight_beams_tick == 39:
            create_beam(pygame.math.Vector2(10, 100), 
                        pygame.math.Vector2(0, 5000),
                        pygame.math.Vector2(336 + self._level.camoffset, -480))

        # Call this function again later for shooting more beams.
        self.fight_beams_tick += 1
        if self.fight_beams_tick < 40:
            self._engine.create_timer(Level13_cave.shoot_beams, 0.05, self, False)

    # Finish shooting beams.
    def finish_shooting_beams(self):
        if self._level.player.alive and not self._level.player.deleted:
            self.fight_state = self.FIGHT_BACK_TO_WAITING_INPUT
            self.fight_box_width = 511
            self.fight_player.draw = False

    # Update Seymour's emotion to make himshocked.
    def update_seymour_emotion(self):
        self.fight_seymour.load("lostlevels/assets/sprites/seymour_skinner_undertale_full_shocked.png")
        self.fight_seymour.set_size(engine.ui.UDim2(0, 75, 0, 192))
        self.fight_move_seymour = False

    # Make Seymour explode.
    def explode_seymour(self):
        # Create the explosion effect.
        self._engine.delete_ui_element(self.fight_seymour)
        self.explosion.play()
        self.fight_flash_bang = effects.create_flash_bang(self._engine)

        # Stop playing Coldplay - My Universe.
        self.my_universe.stop()

        # Conclude the battle after a few seconds.
        self._engine.create_timer(Level13_cave.finish_battle, 4.0, self)

    # Finish the Undertale battle and delete its UI.
    def finish_battle(self):
        # Change the state to the fight ended state.
        self.fight_state = self.FIGHT_ENDED
        
        # Reveal the player, world and scoreboard.
        self._level.player.draw = True
        for ent in self.ground:
            ent.draw = True
        self.trees.draw = True
        self._level.toggle_scoreboard(True)

        # Delete the UI elements and entities for the battle scene.
        if self.fight_started:
            self._engine.delete_ui_element(self.fight_background)
            self._engine.delete_ui_element(self.fight_asterisk)     
            self._engine.delete_ui_element(self.fight_seymour)
            self._engine.delete_ui_element(self.fight_player_dialogue)
            self._engine.delete_ui_element(self.fight_player_enemy_select)
            self._engine.delete_ui_element(self.fight_player_act_select)
            self._engine.delete_ui_element(self.fight_player_remember_talk)
            self._engine.delete_entity(self.fight_left_bar)
            self._engine.delete_entity(self.fight_right_bar)
            self._engine.delete_entity(self.fight_top_bar)
            self._engine.delete_entity(self.fight_bottom_bar)
            self._engine.delete_entity(self.fight_player)
            self._engine.delete_entity(self.fight_freeman)

        # Reset the scoreboard timer and player movement.
        self._level.time_remaining = self.cached_time_remaining
        self._level.player.movetype = engine.entity.MOVETYPE_PHYSICS
        if self._level.player.alive:
            self._level.player.acceleration = 6.5
            self._level.player.can_jump = True
            self._level.player.can_sprint = True
            self._level.player.moveable = True
            self._level.player.always_animate = False
            self._level.can_scroll_left = False

        # If the flash bang effect is still showing, stop it early for comedic
        # effect.
        self.explosion.stop()
        if self.fight_flash_bang:
            self._engine.delete_ui_element(self.fight_flash_bang)

    # Stop playing the ASGORE theme when the player dies, and reveal the player
    # and world again.
    def player_killed(self):
        # Stop playing the ASGORE theme.
        self.asgore_theme.stop()

        # Finish the battle.
        self.finish_battle()

    # Stop playing the longer soundtracks.
    def level_finish(self):
        self.seymour_speech.stop()
        self.asgore_theme.stop()
        self.my_universe.stop()

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
    global has_used_key
    global unlocked_cave_door
    global world_1_1_module

    # Extract the biome and section information from the section name. Verify the
    # biome given and create the level generator using the biome's name. If there 
    # is no delimiter, assume that the biome is winter.
    split = section.split("_", 1)
    if len(split) == 2:
        biome, name = split
    else:
        biome, name = ("cave" if unlocked_cave_door else "winter"), split[0]
    
    # Only create the level generator if we are not forwarding level generation to
    # the world 1-1 module.
    gen = levelgenerator.LevelGenerator(eng, level, biome)

    # If this is the player's first life playing this level, reset the biome music
    # suffix and the has used key and unlocked cave door toggles.
    if first_life:
        biome_music_suffix = ""
        has_used_key = False
        unlocked_cave_door = False

    # If this is not the player's first life playing this level and the higher
    # power has been achieved, replace the player's death sound with a snippet
    # of Coldplay's Fix You.
    elif biome_music_suffix == "_coldplay":
        level.player.death_sound = eng.create_sound("lostlevels/assets/audio/player/death_coldplay.ogg")
        level.player.death_sound.volume = 1

    # If the level has loaded for the first time for the player's current life
    # and the player has not used the key before, reset the holding key counter.
    if first_load and not has_used_key:
        holding_key = False

    # Preload the world 1-1 module.
    if world_1_1_module == None:
        world_1_1_module = lostlevels.scenes.LoadingLevel.load_level_module(1, 1)

    # Nested function for untoggling the holding key and used key counters when
    # using a door.
    def door_used():
        global holding_key
        global has_used_key
        holding_key = False
        has_used_key = True
        return engine.Event.DETOUR_CONTINUE

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

    # Spawn the key if it is being held.
    if holding_key:
        create_smb2_key(True, None)

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
            (f"cave_inside_cave" if unlocked_cave_door else "cave_door", None)
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
        door = gen.generate_door(pygame.math.Vector2(992, -352), 
                                 "underground_fake_underground",
                                 pygame.math.Vector2(64, -350),
                                 holding_key)
        door.get_event("entered").hook(lambda self, name, returnValue: door_used())

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
        
        # If the player came out of the jar section pipe with a key, spawn a 1996 Stock train.
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
        boss.pounce_immediately = holding_key
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

    # Is this the cave entrance section?
    elif name == "door":
        # Create the level data for this section.
        data = Level13_main(eng, level, pygame.math.Vector2(74, -358), biome)

        # Stop the map from scrolling.
        level.max_scroll = 0

        # Create the ground.
        gen.generate_ground(pygame.math.Vector2(0, -416), 18, 2)

        # Create some walls for the cave.
        gen.generate_ground(pygame.math.Vector2(0, 0), height = 11)
        gen.generate_ground(pygame.math.Vector2(576, 0), height = 15)

        # Create a pipe that lets the player go back to the beginning of the level.
        # The biome of the beginning of the level will also be the cave biome.
        gen.generate_pipe_body(pygame.math.Vector2(0, -352), orientation = lostlevels.sprites.PIPE_90)
        gen.generate_pipe_top(pygame.math.Vector2(32, -352), 
                              lostlevels.sprites.PIPE_90, 
                              f"{biome}_1.3.main")

        # If the player achieved the higher power, create a door that the player can enter 
        # to the next section if they are also holding a key.
        if biome_music_suffix == "_coldplay":
            door = gen.generate_door(pygame.math.Vector2(512, -352), 
                                     "cave_inside_cave",
                                     pygame.math.Vector2(3, -358),
                                     holding_key)
            door.get_event("entered").hook(lambda self, name, returnValue: door_used())

        # Return the level data for this section.
        return data

    # Is this the inside entrance section?
    elif name == "inside_cave":
        # Create the level data for this section.
        data = Level13_cave(eng, level, pygame.math.Vector2(3, -358), biome)

        # Allow the player to scroll leftwards.
        level.can_scroll_left = True

        # Prevent the player from being able to jump or sprint, but make them accelerate
        # faster.
        level.player.acceleration = 20.0
        level.player.can_jump = False
        level.player.can_sprint = False

        # Create the ground.
        data.ground = gen.generate_ground(pygame.math.Vector2(0, -416), 40, 2)

        # Create an unusable door that the player spawns out of.
        gen.generate_door(pygame.math.Vector2(0, -352))

        # Create some walls for the cave.
        gen.generate_blocks(pygame.math.Vector2(0, 0), height = 11)
        gen.generate_blocks(pygame.math.Vector2(1280, 0), height = 15)

        # Create some trees sampled from Undertale's Snowdin.
        # TODO: re-write entity activation code in level scene so that I don't have to
        # manually activate entities like this or 1996 Stock?
        trees = eng.create_entity_by_class("sprite", eng.entity_head())
        trees.load("lostlevels/assets/sprites/undertale_snowdin_trees.png", (1280, 120), 1)
        trees.set_baseorigin(pygame.math.Vector2(0, -296))
        trees.movetype = engine.entity.MOVETYPE_NONE
        eng.activate_entity(trees)
        data.trees = trees

        # Create Seymour Skinner.
        seymour = eng.create_entity_by_class("sprite")
        seymour.load("lostlevels/assets/sprites/seymour_skinner.png", (50, 128), 1)
        seymour.set_baseorigin(pygame.math.Vector2(896, -288))
        seymour.movetype = engine.entity.MOVETYPE_NONE
        data.seymour = seymour

        # Create a pipe after Seymour Skinner that takes the player to the first flagpole
        # in the end-of-level section.
        gen.generate_pipe_body(pygame.math.Vector2(1216, -384))
        gen.generate_pipe_top(pygame.math.Vector2(1216, -352), section = f"winter_end",
                              player_offset = pygame.math.Vector2(1290, 0))

        # Toggle the unlocked cave door counter.
        unlocked_cave_door = True

        # Prevent the level from scrolling beyond the pipe at the end.
        level.max_scroll = 704

        # Return the level data for this section.
        return data
    
    # Is this the end-of-level section?
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
        falling_platform = gen.generate_platform(pygame.math.Vector2(640, -416), 4)
        def platform_fall():
            if (level.player.get_baseorigin().x > 608 
                and falling_platform[0].movetype == engine.entity.MOVETYPE_CUSTOM):
                for ent in falling_platform:
                    ent.movetype = engine.entity.MOVETYPE_PHYSICS
        for ent in falling_platform:
            ent.get_event("per_frame").set_func(lambda self: platform_fall())

        # Create another platform that will levitate upwards when the player stands on it.
        rising_platform = gen.generate_platform(pygame.math.Vector2(896, -416), 4)
        for ent in rising_platform:
            ent.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: sample_hooks.rise_on_collide(rising_platform))
        
        # Create the final piece of ground with some troll flagpoles and the real flagpole. The
        # blocks holding the flagpoles should not be collideable if the player has climbed a
        # flagpole already.
        def flagpole_hold_collision(other):
            if other.get_class() == "player" and level.player.climbed_flagpole:
                return False
            return True
        gen.generate_ground(pygame.math.Vector2(1280, -416), 100, 2)
        blocks = gen.generate_blocks(pygame.math.Vector2(1280, -384))
        blocks.extend(gen.generate_blocks(pygame.math.Vector2(1344, -384)))
        blocks.extend(gen.generate_blocks(pygame.math.Vector2(1376, -384)))
        gen.generate_flagpole(pygame.math.Vector2(1290, -106), spiked = True, troll = True)
        gen.generate_flagpole(pygame.math.Vector2(1322, -138))
        gen.generate_flagpole(pygame.math.Vector2(1354, -106), spiked = True, troll = True)
        gen.generate_flagpole(pygame.math.Vector2(1386, -106), spiked = True, troll = True)
        for block in blocks:
            block.get_event("collision").set_func(
                lambda hit, other, coltype, coldir: flagpole_hold_collision(other))

        # Create some clouds.
        gen.generate_cloud(pygame.math.Vector2(288, -128))
        gen.generate_cloud(pygame.math.Vector2(608, -96))
        gen.generate_cloud(pygame.math.Vector2(896, -128), 4)
        gen.generate_cloud(pygame.math.Vector2(1184, -96), 3)

        # Disable scrolling beyond the flagpole.
        level.max_scroll = 1008

        # Create a wall beyond the flagpole as well so that the player cannot progress beyond the map.
        gen.generate_ground(pygame.math.Vector2(1616, 0), height = 15)

        # Return the level data generated for this section.
        return data

    # The 7th pipe may've been used, so forward all remainder section loading code to the world 1-1
    # module.
    else:
        return world_1_1_module.load_leveldata(eng, level, section, first_life, first_load)