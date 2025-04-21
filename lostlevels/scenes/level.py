"""The actual level scene!"""

import os
import pygame
import engine
import time

from .. import levelinfo
from ..sprites import Moveable

# Level scene.
class Level(engine.Game):
    # Construct the level map.
    def __init__(self, eng, game, section = "main", offset = None, time_remaining = 200):
        # Initialize the game interface.
        super().__init__(eng)
        self.__game = game
        self._engine.console.log(
            f"[Lost Levels]: loading section \"{section}\" from world {game.world}-{game.level}")

        # Declare some of the fundamental level props in advance.
        self.backgroundmain = None
        self.backgroundsecondary = None

        # Declare the audio attributes in advance.
        self.audio_intro = None
        self.audio_main = None
        self.finished_score = self._engine.create_sound(
            "lostlevels/assets/audio/objects/flagpole_count.ogg")
        self.finished_score.volume = 1

        # Has the level concluded yet?
        self.finished = False

        # Generate the world by calling the module's load_leveldata() function.
        self.max_scroll = -1
        self.leveldata = game.levelmodule.load_leveldata(self._engine, self, section)
        if not self.leveldata:
            self._engine.console.error(
                f"[Lost Levels]: invalid section name \"{section}\" for world {game.world}-{game.level}!")

        # Create the player entity at the given offset.
        self.player = self._engine.create_entity_by_class("player")
        self.player.set_baseorigin(offset if offset else self.leveldata.player_offset)
        self.player.level = self
        self._engine.activate_entity(self.player)

        # Create a wall to prevent the player from walking out of the map.
        self.leftwall = self._engine.create_entity_by_class("rect")
        self.leftwall.set_hitbox(pygame.math.Vector2(10, 480))
        self.leftwall.set_baseorigin(pygame.math.Vector2(-10, 0))
        self.leftwall.draw = False
        self._engine.activate_entity(self.leftwall)

        # Create a nested function for handling left wall collision.
        def leftwall_collision(self_wall, other, coltype, coldir):
            if other != self.player:
                return False
            return True
        self.leftwall.get_event("collision").set_func(leftwall_collision)

        # Configure the camera offset.
        self.camoffset = max(self.player.get_baseorigin().x - 64, 0)
        self.scroll_map()

        # Create the level timer.
        self.time_remaining = time_remaining

        # Create a buffer for the last 10 key inputs registered.
        self.last_keys = [None] * 10
        self.last_key_press = 0

        # Create a prompt dialogue for when the player hits the ESC key
        # for the first time.
        self.esc_prompt = self._engine.create_ui_element_by_class("text")
        self.esc_prompt.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.esc_prompt.set_size(engine.ui.UDim2(1, 0, 0, 20))
        self.esc_prompt.set_position(engine.ui.UDim2(0, 0, 1, -50))
        self.esc_prompt.set_text("HIT ESC AGAIN TO RETURN TO LEVEL SELECTION")
        self.esc_prompt.set_colour(pygame.Color(255, 255, 255))
        self.esc_prompt.set_x_align(engine.ui.X_CENTRE)

    # Get the save from the game object.
    def get_save(self):
        return self.__game.save
    
    # Load a new level section.
    def load_newlevel(self, section, offset, time_remaining):
        self.__game.load_level(section, offset, time_remaining)
        
    # Forward the per-frame event to the level data object.
    def per_frame(self):
        self.leveldata.per_frame()

    # Handle the game from behind the scenes, such as scrolling the map.
    def post_physics(self):
        # Only handle triggering the death sequence if the game ran out of time or if the 
        # player entity was destroyed if the level has been completed.
        if not self.finished:
            # If the player is entity has been deleted, initiate the death sequence.
            if self.player.deleted and self.player.can_die:
                self.death()

            # Subtract from the time remaining.
            if self._engine.physics_enabled:
                self.time_remaining = max(self.time_remaining - self._engine.globals.frametime, 0)
                if self.time_remaining == 0 and self.player.alive:
                    self.death()

        # Set the camera offset based on the position of the player.
        player_centre = (576 / 2) - (24 / 2)
        player_x = self.player.get_absorigin().x
        if player_x > player_centre:
            self.camoffset += player_x - player_centre
            if self.max_scroll >= 0:
                self.camoffset = min(self.camoffset, self.max_scroll)
        
        # Scroll all the entities and the background.
        if not self.finished:
            self.scroll_map()
        else:
            # If the player entity has scrolled out of the player's viewpoint, 
            # delete it.
            if self.player.get_absorigin().x > 576:
                self._engine.delete_entity(self.player)

        # Handle playing the level music, if it exists.
        if (self.audio_main != None and (self.audio_intro == None or not self.audio_intro.playing())
            and not self.audio_main.playing()):
            self.audio_main.play(True)

        # Enable the ESC prompt based on whether the ESC key was the last key
        # pressed, and if it was pressed recently.
        if self.last_keys[-1] == pygame.K_ESCAPE and time.perf_counter() - self.last_key_press < 3:
            self.esc_prompt.enabled = self.player.alive
        else:
            self.esc_prompt.enabled = False

        # Forward this event to the level data object.
        self.leveldata.post_physics()

    # Scroll the map.
    def scroll_map(self):
        # Set the displacement of all entities.
        ent = self._engine.entity_head()
        while ent:
            # If this is the left wall, scroll it with the player.
            if ent == self.leftwall:
                ent.set_baseorigin(pygame.math.Vector2(self.camoffset - 10, 0))
                ent = ent.next
                continue

            # If this entity is not active, check if it should be activated.
            if not ent.active:
                # Check if this entity is not too far behind the player. If it is,
                # it should be deleted immediately.
                cam_offset = ent.get_baseorigin().x - self.camoffset
                if cam_offset < (864 if not isinstance(ent, Moveable) else 576):
                    if cam_offset - ent.get_hitbox().x < -576:
                        self._engine.delete_entity(ent)
                    else:
                        self._engine.activate_entity(ent)

            # Check if the entity is active.
            if ent.active:
                # Scroll the entity.
                ent.set_origindisp(pygame.math.Vector2(-self.camoffset, 0))

                # If this entity has scrolled far enough to the back, delete it.
                if ent.get_abstopright().x < -576:
                    self._engine.delete_entity(ent)

            # Go to the next entity.
            ent = ent.next

        # Scroll the background slowly based on the camera offset.
        background_offset = self.camoffset / 3
        self.backgroundmain.set_position(
            engine.ui.UDim2(0, ((-background_offset + 1152) % 2304) - 1152, 0, 0))
        self.backgroundsecondary.set_position(
            engine.ui.UDim2(0, ((-background_offset + 2304) % 2304) - 1152, 0, 0))
        
    # Handle playing music for this level.
    def play_music(self, biome):
        # Load the introduction audio if it exists.
        intro_path = f"lostlevels/assets/audio/{biome}/intro.ogg"
        if os.path.isfile(intro_path):
            self.audio_intro = self._engine.create_sound(intro_path)
            self.audio_intro.volume = 1
            self.audio_intro.play()
        
        # Load the main audio.
        self.audio_main = self._engine.create_sound(f"lostlevels/assets/audio/{biome}/main.ogg")
        self.audio_main.volume = 1

    # Stop playing the level music.
    def stop_music(self):
        if self.audio_intro != None:
            self.audio_intro.stop()
            self.audio_intro = None
        if self.audio_main != None:
            self.audio_main.stop()
            self.audio_main = None

    # The death sequence: kill the player (if they are not already being killed) and
    # go back to the loading level screen.
    def death(self):
        # Ignore if the player if already dead.
        if not self.player.alive:
            return

        # Kill the player, stop playing music and decrement the lives counter.
        self.player.kill()
        self.stop_music()
        self.get_save().header.m_sLives -= 1

        # Create a timer that will call the function for loading the laoding level scene
        # in 4 seconds.
        self._engine.create_timer(self.__game.load_world, 4, self.__game.world)

    # Handle any additional user inputs.
    def keydown(self, enum, unicode, focused):
        # Handle pausing the game, if the player is still alive.
        if enum == pygame.K_p and self.player.alive:
            self._engine.physics_enabled = not self._engine.physics_enabled
            if not self._engine.physics_enabled:
                self.leveldata.pause()
            else:
                self.leveldata.unpause()

        # If the last two keys pressed were ESC keys, return to the level selection
        # map, if the player is alive.
        if (self.last_keys[-1] == pygame.K_ESCAPE and enum == pygame.K_ESCAPE
            and (time.perf_counter() - self.last_key_press < 3) and self.player.alive):
            self.stop_music()
            self.__game.load_levelselection()

        # Buffer the latest input.
        self.last_keys.append(enum)
        self.last_keys = self.last_keys[1:]
        self.last_key_press = time.perf_counter()

        # Forward this event to the player.
        self.player.keydown(enum, unicode, focused)

    # Handle the end of the map.
    def finish_level(self):
        # Has the level already just finished?
        if self.finished:
            return

        # Stop the current music from playing and set the finished flag.
        self.stop_music()
        self.finished = True

        # Create the THX Deep Note sound object and play it.
        thx = self._engine.create_sound("lostlevels/assets/audio/objects/flagpole_victory.ogg")
        thx.volume = 1
        thx.play()

        # Create a timer for transferring the remaining time into score points.
        self.finished_score.play(True)
        self._engine.create_timer(self.handle_timer_score, 1 / 30)

        # Handle whether a new level should be started after this level or not.
        if self.get_save().currentlevel[self.__game.world - 1] >= levelinfo.NUM_LEVELS:
            self.get_save().currentlevel[self.__game.world - 1] = levelinfo.NUM_LEVELS + 1
            self._engine.create_timer(self.__game.load_levelselection, 8)
        else:
            self.get_save().currentlevel[self.__game.world - 1] += 1
            self._engine.create_timer(self.__game.load_world, 8, self.__game.world)

    # Handle transferring the remaining time into score points.
    def handle_timer_score(self):
        # Transfer from time remaining into score points.
        self.time_remaining = max(self.time_remaining - 2, 0)
        self.get_save().header.m_uScore += 20

        # Repeat this function call if there is still some time remaining.
        if self.time_remaining > 0:
            self._engine.create_timer(self.handle_timer_score, 1 / 30)
        else:
            self.finished_score.stop()